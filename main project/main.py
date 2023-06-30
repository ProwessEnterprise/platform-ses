from email.message import EmailMessage
from dotenv import load_dotenv
import pymysql.cursors
import pika , sys, os
import json
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

def receive_email():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.exchange_declare(exchange='email_exchange', exchange_type='fanout')
    channel.queue_bind(exchange='email_exchange', queue=queue_name)


    def callback(ch, method, properties, body):
      message = json.loads(body)
      recipient_email = message['recipient_email']
      print("Received recipient_email:", recipient_email)
      main(message)
    
      
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
   


def main(message) :   
    load_dotenv()
    sender_address = os.environ['sender_address']
    sender_password = os.environ['sender_password']
    cc_address = os.environ['cc_address'] . split(',')
    host_name = os.environ['host_name']
    user_name = os.environ['user_name']
    database_password = os.environ['database_password']
    database_name1 = os.environ['database_name1']
    receiver_email = message['recipient_email']
      
    db = EmailDatabase( host_name, user_name, database_password, database_name1)
    db.connect()
    
    email = db.get_receiver1()
    subject = email['subject']
    body = email['body']
    
    send_email(sender_address, sender_password, receiver_email, cc_address, subject, body)
   
   
    
    db.disconnect()


if __name__ == '__main__':
    try:
        receive_email()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0) 