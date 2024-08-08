import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglu.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
import datetime
import time
import awswrangler as wr

args = getResolvedOptions(sys.argv,['JOB_NAME','secret-name','glue-sap-data-table','glue-sap-meta-ata-table','glue-aurora-connection-name'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'],args)
job_run_id = args['JOB_RUN_ID']

def get_parameters(param_key):
    ssm = boto3.client("ssm")
    response = ssm.get_parameters(Names=[param_key,])
    return response['Parameters'][0]['Value']

# secret_name is passed from CloudFormation template
# SSM parameter sapHanauserName, sapHanaPassword and sapJdbcURL should exist in Secrets Manager.

def get_secret_info():
    secret_id = args['secret_name']
    client = boto3.client("secretsmanager")
    get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    userName = secret.get('sapHanauserName')
    password = secret.get('sapHanaPassword')
    jdbcURL = secret.get('sapJdbcURL')
    return userName, password, jdbcURL

def write_jobstart_metadata(number_of_records):
    data = [{"job_name":job_run_id,"job_status":'started',"created_by":'glue-SAP-Ingestion',"create_time":datetime.datetime.now()}]
    df = spark.createDataFrame(data)
    dyf = DynamicFrame.fromDF(df,glueContext,"name_dyf")
    meta_PostgreSQLtable = glueContext.write_dynamic_frame.from_catalog(
        Frame=dyf,
        database="sap-aurora",
        table_name=args['glue_sap_meta_data_table'],
        transformation_ctx="meta_PostgreSQLtable",
    )

def write_jobend_metadata(number_of_records):
    data = [{"job_name":job_run_id,"job_status":'ended',"created_by":'glue-SAP-Ingestion',"create_time":datetime.datetime.now()}]
    df = spark.createDataFrame(data)
    dyf = DynamicFrame.fromDF(df,glueContext,"name_dyf")
    meta_PostgreSQLtable = glueContext.write_dynamic_frame.from_catalog(
        Frame=dyf,
        database="sap-aurora",
        table_name=args['glue_sap_meta_data_table'],
        transformation_ctx="meta_PostgreSQLtable",
    )

def delete_previous_table_data():
    con = wr.postgresql.connect(args['glue_aurora_connection_name'])
    with con.cursor() as cursor:
        cursor.execute("delete FROM materials")
    con.commit()
    con.close()

def delete_previus_s3_data():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('bucket_name')
    bucket.objects.filter(Prefix="sap-ingestion/data/").delete()

#"SAP-INGESTION-MAPPING" needs to be replaced with actual source and target database mapping value from parameter store.
def movedata_sap_to_aurora():
    table_name = get_parameters("PARAMETER_NAME")
    jdbc_driver_name = "com.sap.db.jdbc.Driver"
    db_username,db_password,db_url = get_secret_info()
    df = glueContext.read.format("jdbc").option("driver", jdbc_driver_name).option("url",db_url).option("dbtable", table_name).option("user", db_username).option("password",db_password).load()
    datasource = DynamicFrame.fromDF(df,glueContext, "datasource")
    ApplyMapping = ApplyMapping.apply(
        frame=datasource,
        mapping=["SAP-INGESTION_MAPPINGS"],
        transformation_ctx="ApplyMapping",
    )
    datasink = glueContext.write_dynamic_frame.from_catalog(frame = ApplyMapping,database="sap-aurora",table_name=args['sap_data_table'], transformation_ctx = "datasink")
    return df.count()

write_jobstart_metadata()
delete_previous_table_data()
number_of_records=movedata_sap_to_aurora()
write_jobend_metadata(number_of_records)
job.commit()