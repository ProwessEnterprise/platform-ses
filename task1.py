from email.message import EmailMessage
from dotenv import load_dotenv
import os
import ssl
import smtplib
load_dotenv()
email_sender = os.environ['EMAIL_ADDRESS1']
email_password = os.environ['EMAIL_PASSWORD1']
email_receiver = 'gottipatisaividhya4280@gmail.com'
subject = 'DOTENV mail'
body = """
generating a automated mail using python"""
em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)
context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
     smtp.login(email_sender, email_password)
     smtp.sendmail(email_sender, email_receiver, em.as_string())