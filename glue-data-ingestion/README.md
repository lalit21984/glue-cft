Summary
Summary
Many customers are building solutions with databases on AWS. SAP customers are no different. Many of these solutions are built around S3 where you ingest data to Glue and transform based on your business case. This guide helps to create SAP Data Ingestion Solution to Aurora Database with the help of AWS Glue and StepFunction. It also refreshes full set of data with the latest version on every run.


Data Volume
Data is extracted from SAP Hana high level view which in turn utilizes a hierarchy of views to get the data. It is difficult to predict the number of records as it varies from customer to customer, however this solution gets ~250k-400k rows after every ingestion.


DynamicFrame - ApplyMapping
In order to perform Database Schema conversion the ApplyMapping class is used. It is a type conversion and field renaming function for your data. Below is the sample mapping that can be referenced:

mapping = [
                   ('old_column1', 'string', 'new_column1', 'bigint' ),
                   ('old_column2', 'int', 'new_column2', 'float')
                   ]


IAM Permissions
 Roles
glue-service-role (role assumed by Glue and StepFunction to run the job)

Policies 

glue-service-policy (utilized by glue-service-role)
This policy provides permission to all the glue resources like Glue Job, Crawler, JDBC connections and other supporting resources like VPC, S3, CloudWatch Log Groups, Secrets Manager etc.

step-function-glue-policy (utilized by glue-service-role)
 Provides permission for the StepFunction to start the Glue Job based on the Event bridge scheduled trigger and send email notification via SNS topic.

Prerequisites and limitations
Prerequisites
An Active AWS account
AWS CLI
AWS VPC
AWS S3
Secrets Manager
Parameter Store
Subnet
Security Groups
Python 3.8
SAP Hana and Aurora SQL DB
Limitations
IAM Roles and Policies are not part of the CloudFormation stack and needs to be created separately.

Architecture


![image](https://github.com/user-attachments/assets/6718f49f-c3e0-4267-8bab-639bd760da5f)



Considerations:
AWS CloudFormation: The create-stack CLI command creates all the resources in the target architecture along with Glue Crawlers which would in turn add the event in CloudTrail for CreateCrawler.

Amazon EventBridge: The scheduled rule triggers the state machine that orchestrates Glue Job and SNS notification delivery. The Event based rule invokes the Lambda function in response to the event in CloudTrail for CreateCrawler. This would eventually start the Crawlers and create the initial database and tables required for the scheduled Glue Job.

AWS Glue: The scheduled Glue Job runs and deletes any existing data from Aurora and replaces it with most recent copy of data from SAP HANA.

Amazon SNS: Once the Glue Job completes it sends an email notification indicating a success or failure.


Tools
AWS Glue - A fully managed extract, transform, and load (ETL) service. It helps you reliably categorize, clean, enrich, and move data between data stores and data streams.

AWS CLI - The AWS Command Line Interface (AWS CLI) is an open-source tool for interacting with AWS services through commands in your command-line shell. With minimal configuration, you can run AWS CLI commands that implement functionality equivalent to that provided by the browser-based AWS Management Console from a command prompt.

AWS CloudFormation - AWS CloudFormation helps you model and set up your AWS resources, provision them quickly and consistently, and manage them throughout their lifecycle. You can use a template to describe your resources and their dependencies, and launch and configure them together as a stack, instead of managing resources individually. You can manage and provision stacks across multiple AWS accounts and AWS Regions.

Visual Studio Code - Visual Studio Code or any other IDE.






Epics
CSV
Implementation
Story
Description
Skills required
Code

The code can be cloned from below link 

AWS DevOps
IAM Roles and Policies

Following CLI command creates the necessary IAM Roles and Policies:

aws iam create-policy --policy-name glue-service-policy --policy-document file://glue-service-policy.json
aws iam create-policy --policy-name step-function-glue-policy --policy-document file://step-function-glue-policy.json
aws iam create-role --role-name glue-service-role --assume-role-policy-document file://trust-policy.json
aws iam attach-user-policy --user-name glue-service-role --policy-arn arn:aws:iam::XXX:policy/glue-service-policy
aws iam attach-user-policy --user-name glue-service-role --policy-arn arn:aws:iam::XXX:policy/step-function-glue-policy



AWS DevOps
CloudFormation Resources

The CLI command below creates all the AWS Resources and triggers the Glue Crawlers post stack creation is complete.

aws cloudformation create-stack --stack-name <STACK-NAME> --template-body file://cfnTemplate-SAP-Data-Ingestion.yaml
AWS DevOps


Related resources
AWS CloudFormation Documentation

AWS Glue Documentation

AWS StepFunction Documentation

AWS Lambda

Amazon S3 Documentation

AWS-CLI

ApplyMapping Class


Additional information
The overall goal of this pattern is to provide training that will enable delivery teams:

Help SAP customers build Analytics solutions using AWS Platform Services.

Plan and implement a successful data Ingestion solution for SAP customers.

Ensure smooth, consistent, efficient and quick process flow.








# glue-data-ingestion



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://github-repo/glue-data-ingestion.git
git branch -M main
git push -uf origin main
```


## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Automatically merge when pipeline succeeds](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thank you to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README
Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
