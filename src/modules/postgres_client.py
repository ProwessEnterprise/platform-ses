""" Postgres Client """
import logging
import psycopg2
import psycopg2.extras

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class PostgresSQL:
    """ Postgres Class """
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.psql_connection = None
        self.cursor = None

    def connect(self):
        """ Connect to a Postgres database """
         # Connect to an existing database
        self.psql_connection = psycopg2.connect(user=self.user,
                                  password=self.password,
                                  host=self.host,
                                  port="5432",
                                  database=self.database
                                )   
        self.cursor = self.psql_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def disconnect(self):
        """ Disconnect from a Postgres database """
        if self.psql_connection and self.cursor:
            self.cursor.close()
            self.psql_connection.close()
            self.cursor = None
            self.psql_connection = None

    def insert_record(self, table_name, columns, values):
        """ Insert record into a table """
        try:
            self.connect()
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.cursor.execute(insert_query)
            self.psql_connection.commit()
        except (Exception, psycopg2.Error) as error:
            LOGGER.error(f"Error while inserting record into table {table_name}: {error}".format(table_name=table_name,error=error))
        finally:
            self.disconnect()
    def update_record(self, table_name, set_values, where_condition):
        """ Update record in a table """
        try:
            self.connect()
            update_query = f"UPDATE {table_name} SET {set_values} WHERE {where_condition}"
            self.cursor.execute(update_query)
            self.psql_connection.commit()
        except (Exception, psycopg2.Error) as error:
            LOGGER.error(f"Error while updating record in table {table_name}: {error}".format(table_name=table_name,error=error))
        finally:
            self.disconnect()
