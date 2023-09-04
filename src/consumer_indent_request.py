""" RabbitMQ consumer."""
import json
import logging
from email.message import EmailMessage
import smtplib
from dataclasses import dataclass

import dotenv
from basic_client import BasicPikaClient
from postgres_client import PostgresSQL



LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


@dataclass
class ConnectionInfo:
    """ ConnectionInfo class """
    rabbitmq_broker_id: str
    rabbitmq_user: str
    rabbitmq_password: str
    

@dataclass
class DBConnectionInfo:
    """ DBConnectionInfo class """
    host_name: str
    user_name: str
    database_password: str
    database: str


class MessageConsumer(BasicPikaClient, PostgresSQL):
    """ MessageConsumer class """

    def __init__(self, rabbit_mq_info: ConnectionInfo, db_info: DBConnectionInfo):

        BasicPikaClient.__init__(self,
                                 rabbit_mq_info.rabbitmq_broker_id,
                                 rabbit_mq_info.rabbitmq_user,
                                 rabbit_mq_info.rabbitmq_password,
                                 )
        PostgresSQL.__init__(self, db_info.host_name,
                             db_info.user_name,
                             db_info.database_password,
                             db_info.database
                             )
        self._channel = None
        self._queue = None
        self._db = None
        self.body = None
        self._indent_request_data = {"asset_type": None, "asset_id": None,
                            "make": None, "model": None,"os": None,"processor": None,
                            "ram": None, "hdd": None, "ssd": None, "graphics": None,
                            "screen_size": None, "serial_number": None, "warranty": None,
                            "asset_model": None, "dispatch_date": None
                        }
        self._user_data = {"name": None, "email": None, "employee_id": None}
        self._vendor_data = {"name": None, "email": None, "vendor_id": None}

        self.subject = None


    def send_email(self):
        """ send email """
        try:
            email_message = EmailMessage()
            email_message['From'] = EMAIL_ID
            # email_message['cc'] = EMAIL_CC
            email_message['To'] = self._vendor_data["email"]
            email_message['Subject'] = self.subject
            email_message.set_content(self.body, subtype='html')
            with smtplib.SMTP(EMAIL_EXCHANGE, EMAIL_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_ID, EMAIL_PASSWORD)
                smtp.send_message(email_message)
            LOGGER.info("Email sent successfully")
        except Exception as exception:
            print(exception)
            logging.exception("Error occurred while processing email:")

    def prepare_email(self):
        """ prepare email """

        self.subject = "Indent Request"
        body_file_name = "./static/indent-request.html"
        with open(body_file_name, "r") as body_file:
            self.body = body_file.read().format(
                self._vendor_data["name"],
                # self._indent_request_data["asset_id"],
                self._indent_request_data["asset_type"],
                self._indent_request_data["model"],
                self._indent_request_data["make"],
                self._indent_request_data["os"],
                self._indent_request_data["processor"],
                self._indent_request_data["ram"],
                self._indent_request_data["screen_size"]
        )

    def get_vendor_info(self, vendor_id):
        """ get vendor info """
        query = f"SELECT * FROM vendor WHERE id='{vendor_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self._vendor_data["name"] = result["name"]
        self._vendor_data["email"] = result["email"]
        self._vendor_data["vendor_id"] = result["id"]

    def get_indent_request_info(self, indent_request_id):
        """ get indent request info """
        query = f"SELECT * FROM indent_request WHERE id={indent_request_id};"
        LOGGER.info(query)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        LOGGER.info(result)
        self._indent_request_data["asset_type"] = result["asset_type"]
        self._indent_request_data["model"] = result["model"]
        self._indent_request_data["make"] = result["make"]
        self._indent_request_data["os"] = result["os"]
        self._indent_request_data["processor"] = result["processor"]
        self._indent_request_data["ram"] = result["ram"]
        self._indent_request_data["screen_size"] = result["screen_size"]

    def get_user_info(self,user_id):
        """ get user info """
        query = f"SELECT * FROM employee WHERE id='{user_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self._user_data["name"] = result["name"]
        self._user_data["email"] = result["email"]
        self._user_data["employee_id"] = result["employee_id"]


    def on_message_recieve(self, c_h, method, properties, body):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(properties, method, c_h)
        LOGGER.info("Message Received - %s", body)
        message = json.loads(body)
        self.get_vendor_info(vendor_id=message["vendor_id"])
        self.get_indent_request_info(indent_request_id=message["indent_request_id"])
        self.prepare_email()
        self.send_email()

    def consumer_declare(self, queue_name):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(f"Trying to declare queue({queue_name})...".format(
            queue_name=queue_name))
        self._channel = self.connection.channel()
        self._queue = queue_name
        self_result = self._channel.queue_bind(queue='test',exchange="email_exchange")

    def start_consuming(self):
        """ some text"""
        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=self.on_message_recieve,
            auto_ack=True
        )
        try:
            LOGGER.info(" [*] Waiting for messages. To exit press CTRL+C")
            self._channel.start_consuming()
        except KeyboardInterrupt:
            LOGGER.info(" Stopped consuming")
            self._channel.stop_consuming()


if __name__ == "__main__":

    HOSTNAME = dotenv.get_key(".env", "DB_HOST")
    USERNAME = dotenv.get_key('.env', "DB_USER")
    PASSWORD = dotenv.get_key('.env', "DB_PASSWORD")
    DATABASE = dotenv.get_key('.env', "DB_NAME")
    TABLE = dotenv.get_key('.env', "TABLE_NAME")

    RABBITMQ_BROKER_ID = dotenv.get_key(".env", "RABBITMQ_EC2_HOST")
    RABBITMQ_USER = dotenv.get_key(".env", "RABBITMQ_EC2_USER")
    RABBITMQ_PASSWORD = dotenv.get_key(".env", "RABBITMQ_EC2_PASSWORD")
    
    EMAIL_ID = dotenv.get_key(".env", "EMAIL_ID")
    EMAIL_PASSWORD = dotenv.get_key(".env", "EMAIL_PASSWORD")
    EMAIL_CC = dotenv.get_key(".env", "EMAIL_CC")
    EMAIL_EXCHANGE = dotenv.get_key(".env", "EMAIL_EXCHANGE")
    EMAIL_PORT = dotenv.get_key(".env", "EMAIL_PORT")

    basic_message_receiver = MessageConsumer(
        ConnectionInfo(
            RABBITMQ_BROKER_ID,
            RABBITMQ_USER,
            RABBITMQ_PASSWORD
        ),
        DBConnectionInfo(
            HOSTNAME,
            USERNAME,
            PASSWORD,
            DATABASE
        )
    )

    basic_message_receiver.connect()
    basic_message_receiver.consumer_declare("indent_request")
    basic_message_receiver.start_consuming()
    basic_message_receiver.disconnect()
