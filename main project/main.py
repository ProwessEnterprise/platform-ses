from email.message import EmailMessage
from dotenv import load_dotenv
import pymysql.cursors
import os
import ssl
import smtplib

class EmailDatabase:
    def __init__(self, host, user, password, database):
       self.host = host
       self.user = user
       self.password = password
       self.database = database
       self.connection = None
       self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          database=self.database,
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
    
    def get_receiver(self):
        query = "SELECT receiver FROM emails ORDER BY id DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result
    
    def get_receiver1(self):
        query = "SELECT subject, body FROM emailinfo ORDER BY id DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result
    


    
    def disconnect(self):
        if self.connection and self.cursor:
           self.cursor.close()
           self.connection.close()
           self.cursor = None

def send_email(email_sender, email_password, email_receiver, email_cc, subject, body):
        em = EmailMessage()
        em['From'] = email_sender
        em['cc'] = email_cc
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body, subtype='html')
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
          smtp.login(email_sender, email_password)
          smtp.send_message(em)
def main():
    load_dotenv()
    sender_address = os.environ['sender_address']
    sender_password = os.environ['sender_password']
    cc_address = os.environ['cc_address'] . split(',')
    host_name = os.environ['host_name']
    user_name = os.environ['user_name']
    database_password = os.environ['database_password']
    database_name1 = os.environ['database_name1']

    db = EmailDatabase( host_name, user_name, database_password, database_name1)
    db.connect()
    
    email = db.get_receiver()
    receiver_email = email['receiver']
    
    email1 = db.get_receiver1()
    subject = email1['subject']
    body = email1['body']
    send_email(sender_address, sender_password, receiver_email, cc_address, subject, body)


    db.disconnect()

if __name__ == '__main__':
    main()

   





