""" Basic Pika Client for RabbitMQ """
import ssl
import logging
import pika

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class BasicPikaClient():
    """ Basic Pika client """
    def __init__(self, rabbitmq_broker_id, rabbitmq_user, rabbitmq_password):
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        LOGGER.info(f"Rabbit Mq connecting to {rabbitmq_broker_id}")
        parameters = pika.ConnectionParameters(host=rabbitmq_broker_id,
                                               port=5672, credentials=credentials,virtual_host='/')
        self.connection = pika.BlockingConnection(parameters)
        LOGGER.info("Rabbit Mq connected to localhost")

    def close(self):
        """ close connection """
        # self.channel.close()
        self.connection.close()
        LOGGER.info("Rabbit Mq connection closed")
    

# basic = BasicPikaClient('localhost', 'admin', 'admin@123')

