# aws-expense-auditor - Python Lambda

aws-expense-auditor is a lambda function written in python to fetch and report daily AWS cost through email.

## Prerequisite
The lambda function should have IAM permission to access Cost Explorer
The lambda uses smtplib to send emails. So a dedicate email account and its password is needed as environment variables. Also make use to enable "less-secure-app-access" for that gmail account.

## How to Run locally
```
export SENDER_EMAIL=<email>
export SENDER_EMAIL_PASSWD=<password>
export RECEIVER_EMAILS=<receiver_emails>

pip install -r requirements.txt

python lambda.py
```

## Deploying to Lambda
If you are flexible using AWS CLI, make use of the following command to redeploy the code to lambda.

```
pip install -r requirements.txt -t ./

chmod -R 755 .

zip -r ../aws-expense-auditor.zip .

aws lambda update-function-code --function-name <lambda-name> --zip-file fileb://../aws-expense-auditor.zip
```
