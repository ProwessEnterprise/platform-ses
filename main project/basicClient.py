import ssl
import logging
import pika
from pika.exchange_type import ExchangeType

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class BasicPikaClient():

    def __init__(self, rabbitmq_broker_id, rabbitmq_user, rabbitmq_password, region):
        
        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')

        url = f"amqps://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_broker_id}.mq.{region}.amazonaws.com:5671"
        logging.info(f"Rabbit Mq connecting to {url}")
        parameters = pika.URLParameters(url)
        parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        self.connection = pika.BlockingConnection(parameters)
        logging.info(f"Rabbit Mq connected to {rabbitmq_broker_id}")

    def close(self):
        self.channel.close()
        self.connection.close()
        logging.info(f"Rabbit Mq connection closed")
    

    