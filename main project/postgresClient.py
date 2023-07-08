import psycopg2
import logging 

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class PostgresSQL:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.psqlConnection = None
        self.cursor = None

    def connect(self):

         # Connect to an existing database
        self.psqlConnection = psycopg2.connect(user=self.user,
                                  password=self.password,
                                  host=self.host,
                                  port="5432",
                                  database=self.database
                                )     
        self.cursor = self.psqlConnection.cursor()
      
    def disconnect(self):
        if self.psqlConnection and self.cursor:
            self.cursor.close()
            self.psqlConnection.close()
            self.cursor = None
            self.psqlConnection = None
