import pika, sys, os
import json
import pymysql.cursors
from dotenv import load_dotenv
import os
import traceback
import logging
class EmailDatabase1:
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
    
    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS emailinfo(
                   id BIGINT AUTO_INCREMENT PRIMARY KEY,
                   subject VARCHAR(255),
                   body text)"""
        self.cursor.execute(query)
        self.connection.commit()
   
    def insert_emailinfo(self, subject, body):
        query = """INSERT INTO emailinfo(subject, body)
                VALUES(%s,%s)"""
        self.cursor.execute(query,(subject, body))
        self.connection.commit()
    
    def get_all_emailinfo(self):
        query = "SELECT * FROM emailinfo ORDER BY id DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        emails = []
        for row in result:
            email = {
            "id": row['id'],
            "subject": row['subject'],
            "body": row['body']
            }
            emails.append(email)
        return emails
    
    def disconnect(self):
        if self.connection and self.cursor:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
def receive_email(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    result= channel.queue_declare(queue='', exclusive=True )
    queue_name = result.method.queue
    channel.exchange_declare(exchange='email_exchange', exchange_type='fanout')
    channel.queue_bind(exchange='email_exchange', queue=queue_name)
    
    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        print(" [x] Received %r" % message)
        send_email(message)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def send_email(message):
    load_dotenv()
    host_name = os.environ['host_name']
    user_name = os.environ['user_name']
    database_password = os.environ['database_password']
    database_name1 = os.environ['database_name1']

    db = EmailDatabase1(host_name, user_name, database_password, database_name1)
    db.connect()
    db.create_table()

    recipient_name = message['recipient_name']
    employee_id = message['employee_id']
    asset_id = message['asset_id']
    asset_type = message['asset_type']
    asset_model = message['asset_model']
    dispatch_date = message['dispatch_date']

    subject = "Asset Tracking | {} | {} | Employee id: {}".format(asset_type, recipient_name, employee_id)

    if asset_type.lower() == "laptop":
        body_file_name = "laptopbody.html"
    elif asset_type.lower() == "printer":
        body_file_name = "printerbody.html"
    else:
        body_file_name = "modembody.html" 
    
    with open(body_file_name, "r") as body_file:
        body = body_file.read().format(recipient_name, asset_id, asset_type, asset_model, asset_id, dispatch_date)

    try:
        db.insert_emailinfo(subject, body)
        print("Email inserted successfully!")
        logging.info("Email inserted successfully!")

        emails = db.get_all_emailinfo()
        print("ALL EMAILS:")
        print(emails)
    except Exception as e:
        print("Error occurred while processing email:")
        print(traceback.format_exc())  
        logging.exception("Error occurred while processing email:")
 
    db.disconnect()
 
     
def main():
    try:
        logging.basicConfig(filename='email.log', level=logging.INFO)
        receive_email(None)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    main()