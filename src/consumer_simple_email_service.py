""" RabbitMQ consumer."""
import json
import logging
from email.message import EmailMessage
import smtplib
from smtplib import SMTPException
from dataclasses import dataclass

import dotenv
from modules.basic_client import BasicPikaClient
from modules.postgres_client import PostgresSQL


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


@dataclass
class IndentRequestInfo:
    """ IndentRequestInfo class """
    asset_type: str
    model: str
    make: str
    os: str
    processor: str
    ram: str
    screen_size: str
    vendor_name: str

@dataclass
class AssetInfo:
    """ AssetInfo class """
    asset_type: str
    asset_id: str
    asset_model: str


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


    def send_email(self, sender_email, receiver_email, cc_email, subject, body, sender_password):
        """ send email """
        try:
            email_message = EmailMessage()
            email_message['From'] = sender_email
            email_message['cc'] = cc_email
            email_message['To'] = receiver_email
            email_message['Subject'] = subject
            email_message.set_content(body, subtype='html')
            with smtplib.SMTP(EMAIL_EXCHANGE, EMAIL_PORT) as smtp:
                smtp.starttls()
                smtp.login(sender_email, sender_password)
                smtp.send_message(email_message)
            LOGGER.info("Email sent successfully")
        except SMTPException as smtp_error:
            logging.exception(f"Error occurred while processing email: \
                              {smtp_error}".format(smtp_error=smtp_error))

    def prepare_indent_request_email(self, indent_request_info: IndentRequestInfo) -> dict:
        """ prepare indent request email """
        subject = "Indent Request"
        body_file_name = "./static/indent-request/indent-request.html"
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(
                indent_request_info.vendor_name,
                indent_request_info.asset_type,
                indent_request_info.model,
                indent_request_info.make,
                indent_request_info.os,
                indent_request_info.processor,
                indent_request_info.ram,
                indent_request_info.screen_size
            )
        return {"subject": subject, "body": body}

    def prepare_password_update_email(self, user_data) -> dict:
        """ prepare password update info email """
        name = user_data["name"]
        employee_id = user_data["employee_id"]
        subject = f"Password update | {name} | Employee id: {employee_id}"
        body_file_name = "./static/password-update/password-update.html"
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(
                name
            )
        return {"subject": subject, "body": body}

    def prepare_dispatch_info_email(self, asset_info: AssetInfo, user_data) -> dict:
        """ prepare dispatch info email """
        asset_type = asset_info.asset_type
        name = user_data["name"]
        employee_id = user_data["employee_id"]

        subject = f"Asset Tracking | {asset_type} | {name} | Employee id: {employee_id}"
        if asset_info.asset_type.lower() == "laptop":
            body_file_name = "./static/dispatch/laptop.html"
        elif asset_info.asset_type.lower() == "printer":
            body_file_name = "./static/dispatch/printer.html"
        else:
            pass
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(
                user_data["name"],
                asset_info.asset_id,
                asset_info.asset_type,
                asset_info.asset_model,
                asset_info.asset_id
            )
        return {"subject": subject, "body": body}

    def get_vendor_info(self, vendor_id) -> dict:
        """ get vendor info """
        query = f"SELECT * FROM {VENDOR_TABLE} WHERE id='{vendor_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if (result["name"] is None) or (result["email"] is None):
            LOGGER.info("Vendor info not found")
            return None
        return {"name": result["name"], "email": result["email"], "vendor_id": result["id"]}

    def get_indent_request_info(self, indent_request_id) -> dict:
        """ get indent request info """
        query = f"SELECT * FROM {INDENT_TABLE} WHERE id={indent_request_id};"
        LOGGER.info(query)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            LOGGER.info("Indent request info not found")
            return None
        return {"asset_type": result["asset_type"], "model": result["model"],
                "make": result["make"], "os": result["os"], "processor": result["processor"],
                "ram": result["ram"], "screen_size": result["screen_size"],
                "approver_id": result["request_approver_id"]
                }

    def get_user_info(self, user_id) -> dict:
        """ get user info """
        query = f"SELECT * FROM {USER_TABLE} WHERE id='{user_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if (result["name"] is None) or (result["email"] is None) or (result["employee_id"] is None):
            LOGGER.info("User info not found")
            return None
        return {"name": result["name"],
                "email": result["email"],
                "employee_id": result["employee_id"]
                }

    def get_asset_info(self, user_id):
        """ get asset info """
        query = f"SELECT * FROM {ASSET_TABLE} WHERE id='{user_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is None:
            LOGGER.info("Asset info not found")
            return None
        return {"asset_type": result["asset_type"], "asset_id_number": result["asset_id_number"],
                "model": result["model"]
            }

    def on_message_recieve(self, c_h, method, properties, body):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(properties, method, c_h)
        LOGGER.info("Message Received - %s", body)
        message = json.loads(body)
        if message["type"] == "password-update":
            user_data = self.get_user_info(user_id=message["data"]["user_id"])
            # if (user_data is None) or (user_data["email"] is None):
            #     LOGGER.info("User info not found")
            email_data = self.prepare_password_update_email(
                user_data=user_data)
            self.send_email(ADMIN_EMAIL_ID,
                            user_data["email"],
                            ADMIN_EMAIL_CC,
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )
        elif message["type"] == "indent-request":
            vendor_data = self.get_vendor_info(
                vendor_id=message["data"]["vendor_id"])
            indent_request_data = self.get_indent_request_info(
                indent_request_id=message["data"]["indent_request_id"])
            # approver_data = self.get_user_info(user_id=indent_request_data["approver_id"])
            email_data = self.prepare_indent_request_email(
                indent_request_info=IndentRequestInfo(
                    asset_type=indent_request_data["asset_type"],
                    model=indent_request_data["model"],
                    make=indent_request_data["make"],
                    os=indent_request_data["os"],
                    processor=indent_request_data["processor"],
                    ram=indent_request_data["ram"],
                    screen_size=indent_request_data["screen_size"],
                    vendor_name=vendor_data["name"]
                )
            )
            self.send_email(ADMIN_EMAIL_ID,
                            vendor_data["email"],
                            ADMIN_EMAIL_CC,
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )
        elif message["type"] == "dispatch":
            asset_data = self.get_asset_info(
                user_id=message["data"]["asset_id"])
            user_data = self.get_user_info(user_id=message["data"]["user_id"])
            email_data = self.prepare_dispatch_info_email(asset_info=AssetInfo(
                asset_type=asset_data["asset_type"],
                asset_id=asset_data["asset_id_number"],
                asset_model=asset_data["model"]
            ), user_data=user_data
            )
            self.send_email(ADMIN_EMAIL_ID,
                            user_data["email"],
                            ADMIN_EMAIL_CC,
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )
        else:
            pass

    def consumer_declare(self, queue_name):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(f"Trying to declare queue({queue_name})...".format(
            queue_name=queue_name))
        self._channel = self.connection.channel()
        self._queue = queue_name
        self._channel.queue_bind(
            queue=QUEUE_NAME, exchange="email_exchange")

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
    USER_TABLE = "employee"
    VENDOR_TABLE = "vendor"
    INDENT_TABLE = "indent_request"
    DISPATCH_TABLE = "dispatch"
    ASSET_TABLE = "asset"

    RABBITMQ_BROKER_ID = dotenv.get_key(".env", "RABBITMQ_EC2_HOST")
    RABBITMQ_USER = dotenv.get_key(".env", "RABBITMQ_EC2_USER")
    RABBITMQ_PASSWORD = dotenv.get_key(".env", "RABBITMQ_EC2_PASSWORD")
    QUEUE_NAME = dotenv.get_key(".env", "QUEUE_NAME")

    EMAIL_ID = dotenv.get_key(".env", "EMAIL_ID")
    EMAIL_PASSWORD = dotenv.get_key(".env", "EMAIL_PASSWORD")
    EMAIL_CC = dotenv.get_key(".env", "EMAIL_CC")
    EMAIL_EXCHANGE = dotenv.get_key(".env", "EMAIL_EXCHANGE")
    EMAIL_PORT = dotenv.get_key(".env", "EMAIL_PORT")

    ADMIN_EMAIL_ID = dotenv.get_key(".env", "ADMIN_EMAIL_ID")
    ADMIN_EMAIL_PASSWORD = dotenv.get_key(".env", "ADMIN_EMAIL_PASSWORD")
    ADMIN_EMAIL_CC = dotenv.get_key(".env", "ADMIN_EMAIL_CC")

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
    basic_message_receiver.consumer_declare(QUEUE_NAME)
    basic_message_receiver.start_consuming()
    basic_message_receiver.disconnect()
