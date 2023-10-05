""" RabbitMQ consumer."""
import json
import time
import logging
from email.message import EmailMessage
import smtplib
from smtplib import SMTPException
import dotenv
from utils.otp_generator import generate_alphanumeric_otp
from utils.data_classes import ConnectionInfo, DBConnectionInfo, SignupOtpInfo, RegisterCompleteInfo

from modules.basic_client import BasicPikaClient
from modules.postgres_client import PostgresSQL

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


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

    def send_email(self, sender_email, receiver_email, subject,
                   body, sender_password, cc_email=None):
        """ send email """
        try:
            print (sender_email, receiver_email, subject, sender_password, cc_email)
            email_message = EmailMessage()
            email_message['From'] = sender_email
            if (cc_email is not None):
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

    def prepare_sigup_otp_email(self, signup_otp_info: SignupOtpInfo) -> dict:
        """ prepare signup otp email """
        subject = "Signup | Authentication | Asset Management"
        body_file_name = "./static/onboard/signup-otp.html"
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(
                signup_otp_info.signup_user,
                signup_otp_info.otp
            )
        return {"subject": subject, "body": body}

    def prepare_register_complete_email(self, account_name ) -> dict:
        """ prepare signup otp email """
        subject = "Registration Completed Successfully | Asset Management"
        body_file_name = "./static/onboard/signup-complete.html"
        print (account_name)
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(account_name)
        return {"subject": subject, "body": body}
    
    def prepare_dispatch_arpprove_email(self, account_name ) -> dict:
        """ dispatch approve email """
        subject = "Dispatch Approved | Asset Management"
        body_file_name = "./static/onboard/dispatch-approve.html"
        print (account_name)
        with open(body_file_name, "r", encoding="UTF-8") as body_file:
            body = body_file.read().format(account_name)
        return {"subject": subject, "body": body}

    def get_signup_user(self,signup_user_email,condition) -> dict:
        """ get asset info """
        time.sleep(2)
        query = f"SELECT * FROM {PLATFORM_USER_TABLE} WHERE {condition} AND email='{signup_user_email}'"
        print (query)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        print (result)
        if result is None:
            LOGGER.info("No signup user found")
            return None
        return {"signup_user": signup_user_email.split("@")[0],
                "email": result["email"], "name": result["name"]}
    
    def get_account_user_info(self, account_name_id) -> dict:
        """ get asset info """
        time.sleep(2)
        query = f"SELECT * FROM {ACCOUNT_TABLE} WHERE account_name_id='{account_name_id}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result is None:
            LOGGER.info("No accounts found")
            return None
        
        data = {"admin_email": None,"account_name": None,"asset_admin_email": None}
        print (result)
        for row in result:
            if row["role"] == "ADMIN":
                data["admin_email"] = row["email"]
                data["account_name"] =  row["name"]
            elif row["role"] == "ASSET_ADMIN":
                data["asset_admin_email"] = row["email"]
            else:
                pass
        return data


    def on_message_recieve(self, c_h, method, properties, body):
        """Called when a message is received. Log message and ack it."""
        LOGGER.info(properties, method, c_h)
        LOGGER.info("Message Received - %s", body)
        message = json.loads(body)
        if message["type"] == "signup-otp":
            condition = "(account_user_status='SIGNUP_INITIATED' OR account_user_status='SIGNUP_OTP_SENT')"
            signup_user_data = self.get_signup_user(message['data']['email'],condition)
            otp = generate_alphanumeric_otp()
            email_data = self.prepare_sigup_otp_email(SignupOtpInfo(
                signup_user=signup_user_data["signup_user"],
                otp=otp
                )
            )
            self.send_email(ADMIN_EMAIL_ID,
                            signup_user_data["email"],
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )
            query = f"UPDATE {PLATFORM_USER_TABLE} SET otp='{otp}',account_user_status='SIGNUP_OTP_SENT' WHERE email='{signup_user_data['email']}'"
            print (query)
            self.cursor.execute(query=query)
            self.psql_connection.commit()
        elif message["type"] == "register-complete":
            condition = "account_user_status='SIGNUP_COMPLETED'"
            platform_user_data = self.get_signup_user(message['data']['email'],condition)
            print (platform_user_data)
            email_data = self.prepare_register_complete_email(platform_user_data["name"])
            self.send_email(ADMIN_EMAIL_ID,
                            platform_user_data["email"],
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )
        elif message["type"] == "dispatch-approve":
            account_user_data = self.get_account_user_info(message['data']['email'])
            print (account_user_data)
            email_data = self.prepare_dispatch_arpprove_email(account_user_data["account_name"])
            self.send_email(ADMIN_EMAIL_ID,
                            account_user_data["email"],
                            email_data["subject"],
                            email_data["body"],
                            ADMIN_EMAIL_PASSWORD
                            )

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
    PLATFORM_USER_TABLE = "platform_user"
    ACCOUNT_TABLE = "account_user"

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
