from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
from postgresClient import PostgresSQL
from basicClient import BasicPikaClient
from email.message import EmailMessage
import smtplib
import ssl


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class MessageConsumer(BasicPikaClient,PostgresSQL):

    def __init__(self,rabbitmq_broker_id, rabbitmq_user, rabbitmq_password, region, host_name,
        user_name,database_password,database ):

        BasicPikaClient.__init__(self, rabbitmq_broker_id, rabbitmq_user, rabbitmq_password, region)
        PostgresSQL.__init__(self, host_name,user_name,database_password,database) 
        self._channel = None
        self._queue = None
        self._db = None
        self.body = None
        self._asset_data = {"asset_type":None,"asset_id":None,"asset_model":None,"dispatch_date":None}
        self._user_data = {"name":None,"email":None,"employee_id":None}
        self.subject = None

    def sendEmail(self):

        try:
            email_sender = "btsot714369@gmail.com"
            email_password = "btmr dkwn cezp iojd"
            email_cc = "kotesh.i@prowessenterprise.com,murthy.k@prowessenterprise.com"

            em = EmailMessage()
            em['From'] = email_sender
            em['cc'] = email_cc
            em['To'] = self._user_data["email"]
            em['Subject'] = self.subject
            em.set_content(self.body, subtype='html')
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.send_message(em)
            logging.info(f'Email Sent to {self._user_data["email"]}')
        except Exception as e:
            print (e)
            logging.exception("Error occurred while processing email:")

    def prepareEmail(self):
        self.subject = "Asset Tracking | {} | {} | Employee id: {}".format(self._asset_data["asset_type"],self._user_data["name"], self._user_data["employee_id"])

        if self._asset_data["asset_type"].lower() == "laptop":
            body_file_name = "./static/laptopbody.html"
        elif self._asset_data["asset_type"].lower() == "printer":
            body_file_name = "./static/printerbody.html"
        else:
            body_file_name = "./static/modembody.html"

        print (self._user_data,self._asset_data)
        
        with open(body_file_name, "r") as body_file:
            self.body = body_file.read().format(
                self._user_data["name"], 
                self._asset_data["asset_id"], 
                self._asset_data["asset_type"], 
                self._asset_data["asset_model"], 
                self._asset_data["asset_id"], 
                self._asset_data["dispatch_date"]
            )

    def getUserInfo(self,user_id):
        query = f"SELECT * FROM user_details WHERE id='{user_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self._user_data["name"] = result["name"]
        self._user_data["email"] = result["email"]
        self._user_data["employee_id"] = result["employee_id"]

    def getDispatchInfo(self,asset_id):
        query = f"SELECT * FROM dispatch WHERE asset_id='{asset_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        print (result)
        self._asset_data["dispatch_date"] =  str(result["date_of_dispatch"])
    
    def getAssetInfo(self,user_id):
        query = f"SELECT * FROM asset WHERE id='{user_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self._asset_data["asset_type"]  =  result["asset_type"]
        self._asset_data["asset_id"]    =  result["asset_id_number"]
        self._asset_data["asset_model"] =  result["model"]

    def onMessageReceive(self,ch, method, properties, body):
        LOGGER.info(f"Message Received - ({body})...")
        message = json.loads(body)
        asset_id = message['asset_id']
        user_id = message["user_id"]
        self.getUserInfo(user_id)
        self.getAssetInfo(asset_id)
        self.prepareEmail()
        self.sendEmail()

    def consumerDeclare(self,queue_name):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(f"Trying to declare queue({queue_name})...") 
        self._channel = self.connection.channel()
        self._queue = queue_name
        self_result = self._channel.queue_bind(queue='test',exchange="email_exchange")

    def startConsuming(self):
        """ some text"""
        self._channel.basic_consume(
                        queue=self._queue, 
                        on_message_callback=self.onMessageReceive, 
                        auto_ack=True
                    )
        
        try:
            LOGGER.info(f" [*] Waiting for messages. To exit press CTRL+C") 
            self._channel.start_consuming()
        except KeyboardInterrupt:
            LOGGER.info(f" Stopped consuming") 
            self._channel.stop_consuming()

if __name__ == "__main__":

    host_name = "localhost"
    user_name = "postgres"
    database_password = "astM@1234"
    database = "prowess_asset_manage"
    asset_table = "asset"
    user_table = "user_details"

    basic_message_receiver = MessageConsumer(
        "b-dd0c2f43-8d03-40c8-8272-ea7a1c07a93d",
        "root",
        "rootUser@1234",
        "us-east-1",
        host_name,
        user_name,
        database_password,
        database
    )
    basic_message_receiver.connect()
    basic_message_receiver.consumerDeclare("test")
    basic_message_receiver.startConsuming()
    
        
