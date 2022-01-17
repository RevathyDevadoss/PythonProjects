import sys
import logging
from logging.handlers import RotatingFileHandler
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import splunk.entity as entity
import splunk.secure_smtplib as secure_smtplib
from splunk.rest import simpleRequest
from email.mime.base import MIMEBase
from email import encoders
import csv
import gzip


# Defining the class
class Alert(object):

    def create_html_template(content):
        mail_template_filled = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ' \
                               '>\n<html ' \
                               '>\n <head>\n  <meta http-equiv="Content-Type" ' \
                               'content="text/html; charset=UTF-8" />\n  <title>\n HTML email\n</title>\n  <meta ' \
                               'name="viewport" content="width=device-width, ' \
                               'initial-scale=1.0"/>\n</head>\n<body>\n%s\n</body>\n</html>\n ' % content
        return mail_template_filled


# Setting Up logger
def setup_logger(level):
    logger = logging.getLogger('my_search_command')
    logger.propagate = False  # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)
    file_handler = logging.handlers.RotatingFileHandler('emailtriggerscript.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger(logging.INFO)


# Function to Send mail
def send_mail(email_message, to_mail, cc_mail, from_mail, mailserver="localhost", subject="Message from python script"):
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(email_message, 'html'))
    attachment = open(file_name, 'rb')
    part1 = MIMEBase('application', 'octet-stream')
    part1.set_payload((attachment).read())
    encoders.encode_base64(part1)
    part1.add_header('Content-Disposition', 'attachment', filename="UserNames.csv")
    msg['To'] = to_mail
    msg['CC'] = cc_mail
    msg['Subject'] = subject
    msg.attach(part1)

    try:
        smtp = secure_smtplib.SecureSMTP(host=mailserver)
        # Check if CC field is empty
        if cc_mail is not None:
            rcpts = cc_mail.split(",") + [to_mail]
        else:
            rcpts = [to_mail]
            # Clear leading / trailing whitespace from recipients
            rcpts = [r.strip() for r in rcpts]

        smtp.sendmail(from_mail, rcpts, msg.as_string())
        logger.info(
            'Custom_Alert_Action_Logs: Script_Name="emailtrigger.py" App_Name="%s" Alert_Name="%s" Owner="%s" Recipients="%s"',
            app, search_name, owner, rcpts)
        logger.info(csv_reader)
        smtp.quit()
    except Exception as e:
        logger.error(str(e))


# Function to create html template for the text recieved from SPLUNK alert UI
def create_html_template(content):
    mail_template_filled = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ' \
                           '>\n<html ' \
                           '>\n <head>\n  <meta http-equiv="Content-Type" ' \
                           'content="text/html; charset=UTF-8" />\n  <title>\n HTML email\n</title>\n  <meta ' \
                           'name="viewport" content="width=device-width, ' \
                           'initial-scale=1.0"/>\n</head>\n<body>\n%s\n</body>\n</html>\n ' % content
    return mail_template_filled


if __name__ == "__main__":
    try:
        alerts = []

        # Read Payload from the splunk
        data = sys.stdin.read()
        parsed_result = json.loads(data)

        # Read the result and configuration data
        owner = parsed_result["owner"]
        app = parsed_result["app"]
        csv_gzip_location = parsed_result["results_file"]
        search_name = parsed_result["search_name"]
        session_key = parsed_result["session_key"]
        result = parsed_result["result"]
        User_Name = result.get('User_Name')
        Days_to_exp = result.get('Days_to_exp')
        Exp_date = result.get('Exp_date')
        configuration = parsed_result["configuration"]
        to_mail = configuration.get('to_mail')
        cc_mail = configuration.get('cc_mail')
        from_mail = configuration.get('from')
        subject = configuration.get('subject')
        txt = configuration.get('msgs')

        with (gzip.open(csv_gzip_location, 'rb')) as csv_reader:
            data = csv.reader(csv_reader)
            for row in data:
                n = 1
                if n == 2:
                    SFT_User_Name = str(row[2]).split()
                    User_email = str(row[3]).split()
                    Password_Exp_Date = str(row[4]).split()
                    Next_Update_Date = str(row[5]).split()
                    WorkGroup_Name = str(row[0])
                    WorkGroup_Primary_Contact = str(row[1])
                else:
                    n == n + 2
            with open('new_data.csv', 'w') as csv_file:
                header = ['WorkGroup_Name', 'WorkGroup_Primary_Contact', 'SFT_User_name', 'User_email',
                          'Password_Exp_Date', 'Next_Update_Date']
                writer = csv.DictWriter(csv_file, fieldnames=header)
                writer.writeheader()
                for uname, uemail, upass, udate in zip(SFT_User_Name, User_email, Password_Exp_Date, Next_Update_Date):
                    writer.writerow(
                        {'WorkGroup_Name': WorkGroup_Name, 'WorkGroup_Primary_Contact': WorkGroup_Primary_Contact,
                         'SFT_User_Name': uname, 'User_email': uemail, 'Password_Exp_Date': upass,
                         'Next_Update_Date': udate})

        file_name = "new_data.csv"

        # Assign html formatted text to set email body
        message = create_html_template(txt)

        # Get the mailserver
        uri = entity.buildEndpoint(
            [
                'saved',
                'searches',
                '_new'
            ],
            namespace=app,
            owner=owner
        )
        responseHeaders, responseBody = simpleRequest(uri, method='GET', getargs={'output_mode': 'json'},
                                                      sessionKey=session_key)
        savedSearch = json.loads(responseBody)
        ssContent = savedSearch['entry'][0]['content']
        mail_server = ssContent.get('action.email.mailserver', 'localhost')
        try:
            f = open('email_content.html', 'w')
            f.write(txt)
            send_mail(to_mail=to_mail, from_mail=from_mail, cc_mail=cc_mail, email_message=txt, mailserver=mail_server,
                      subject=subject)
        except:
            logger.exception('Failed sending email')
    except Exception as e:
        logger.exception("Failed while getting the information for the email")
