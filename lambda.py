import csv
import os
import boto3
import datetime
import smtplib
from datetime import datetime, timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEBase
from email import encoders
import email
import logging


def get_today_and_yesterday_date():
    today = datetime.strftime(datetime.now(), '%Y-%m-%d')
    yesterady = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    return (str(today), str(yesterady))


def save_as_csv(data):
    with open("/tmp/report.csv", "w+") as cost_report:
        csvWriter = csv.writer(cost_report, delimiter=',')
        csvWriter.writerows(data)


def send_email():
    sender_email = os.environ["SENDER_EMAIL"]
    sender_email_passwd = os.environ["SENDER_EMAIL_PASSWD"]
    receiver_emails = os.environ["RECEIVER_EMAILS"]
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(sender_email, sender_email_passwd)

    msg = MIMEMultipart()
    msg['Subject'] = "AWS daily cost report for day " + str(date.today()) 
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_emails)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("/tmp/report.csv", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="report.csv"')
    msg.attach(part)
    smtpserver.sendmail(sender_email, receiver_emails, msg.as_string())


def lambda_handler(event=None, context=None): 
    #Check if the environemnt variables are set
    for var in ["SENDER_EMAIL", "SENDER_EMAIL_PASSWD", "RECEIVER_EMAILS"]: 
        if var not in os.environ:
            logging.error("Missing environemnt variable %s", (var))

    #Initializing Cost Explorer client
    ce_client = boto3.client("ce")
    
    # Date in format yyyy-MM-DD 
    today_date, yesterday_date = get_today_and_yesterday_date()
    
    # Fetching the cost report using CE client
    report = ce_client.get_cost_and_usage( 
        TimePeriod={ 
            "Start": yesterday_date, 
            "End": today_date }, 
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
        Granularity="DAILY", 
        Metrics=[ "UnblendedCost",] 
    )

    #Constructing report CSV
    cost_metrics = list()
    cost_sum = 0
    report = report["ResultsByTime"][0]["Groups"]
    for line_item in report:
        amount = line_item["Metrics"]["UnblendedCost"]["Amount"]
        cost_sum = cost_sum + float(amount)
        key = line_item["Keys"][0]
        cost_metrics.append([key, amount])
    cost_metrics.append(["Total Cost", str(cost_sum)])

    #Save the cost metric data to CSV file
    save_as_csv(cost_metrics) 

    #Send the report CSV through email
    send_email()
    logging.info("Report sent to the target email addresses")


if __name__ == '__main__':
    lambda_handler()