import os
import time
import click
import logging
import psycopg2
from datetime import datetime

def setup_logger(name, base_dir=os.getcwd(), level=logging.INFO):
   log_dirname = 'log'
   log_subdirname = datetime.now().strftime("%Y-%m-%d")
   log_dir = os.path.join(base_dir, log_dirname, log_subdirname)

   if not os.path.exists(os.path.join(base_dir, log_dirname)):
      os.mkdir(os.path.join(base_dir, log_dirname))

   if not os.path.exists(log_dir):
      os.mkdir(log_dir)

   fhandler = logging.FileHandler(os.path.join(log_dir, f'{name}.{datetime.now().strftime("%H:%M:%S")}.log'))
   shandler = logging.StreamHandler()

   fhandler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'))
   shandler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'))

   logger = logging.getLogger(name)
   logger.setLevel(level)

   logger.addHandler(fhandler)
   logger.addHandler(shandler)
   
   return logger

class pg:
    def __init__(self, host, dbname, user, password, timeout, port, logger):
        self.connection = None
        self.cursor = None

        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.timeout = timeout
        self.port = port
        self.connection_string = f'host={host} port={port} dbname={dbname} user={user} password={password} connect_timeout={timeout}'

        self.logger = logger


    def dict_factory(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}
    
    def open(self):
        try:
            self.connection = psycopg2.connect(self.connection_string)
            self.connection.row_factory = self.dict_factory
            self.cursor = self.connection.cursor()
        except psycopg2.Error:
            self.logger.error("UNABLE TO CONNECT TO DATABASE", exc_info=True)
    
    def close(self):  
        if not self.connection:
            return
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.close()

    def exec_query(self, sql, params=[]):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()


def prepare_db(host, dbname, user, password, timeout, master_port, logger):   
   with pg(host, dbname, user, password, timeout, master_port, logger) as db:
      db.exec_query('CREATE OR IGNORE TABLE hatest(timestamp TM)')

def test(host, dbname, user, password, timeout, master_port, replica_port, logger):
   data = int(time.time())
   logger.info(f'ATTEMPT TO INSERT TEST DATA: {data}')
   with pg(host, dbname, user, password, timeout, master_port, logger) as db:
      inserted = db.exec_query('INSERT INTO hatest VALUES(CURRENT_TIMESTAMP())')[0]
      logger.info(f'INSERTED: {inserted}')
      
   logger.info(f'ATTEMPT TO RETRIVE TEST DATA: {data}')
   with pg(host, dbname, user, password, timeout, replica_port, logger) as db:
      retrived = db.exec_query('SELECT MAX() FROM hatest')[0]
      logger.info(f'RETRIVED: {retrived}')
      
   logger.info(f'TEST DATA: {data}; INSERTED: {inserted}; RETRIVED: {retrived}; TEST SUCCESSFULL: {data == inserted == retrived}')

@click.command()
@click.option('-h', '--host', type=str, default='127.0.0.1', show_default=True, help='haproxy host')
@click.option('-d', '--dbname', type=str, default='postgres', show_default=True)
@click.option('-u', '--user', type=str, default='postgres', show_default=True)
@click.option('-p', '--password', type=str)
@click.option('-t', '--timeout', type=int, default=5, show_default=True, help='Connection timeout')
@click.argument('master_port')
@click.argument('replica_port')
def main(host, dbname, user, password, timeout, master_port, replica_port):
   logger = setup_logger('patroni-tester')
   prepare_db(host, dbname, user, password, timeout, master_port, logger)
   # while True:
   test(host, dbname, user, password, timeout, master_port, replica_port, logger)

if __name__ == "__main__":
   main()

