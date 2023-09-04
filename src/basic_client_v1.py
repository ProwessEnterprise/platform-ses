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
    def __init__(self, rabbitmq_broker_id, rabbitmq_user, rabbitmq_password, region):
        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
        url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:15672"
        print (url)
        LOGGER.info("Rabbit Mq connecting to %s", url)
        parameters = pika.URLParameters(url)
        parameters.ssl_options = pika.SSLOptions(context=ssl_context)
        self.connection = pika.BlockingConnection(parameters)
        LOGGER.info("Rabbit Mq connected to %s", url)

    def close(self):
        """ close connection """
        # self.channel.close()
        self.connection.close()
        LOGGER.info("Rabbit Mq connection closed")
    
    