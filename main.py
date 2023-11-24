#!/usr/bin/python3
import os
import click
import logging
import psycopg2
from time import sleep
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

   fhandler.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s'))
   shandler.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s'))

   logger = logging.getLogger(name)
   logger.setLevel(level)

   logger.addHandler(fhandler)
   logger.addHandler(shandler)
   
   return logger
 
class node_data:
   def __init__(self, master, addr):
      self.master = master
      self.addr = addr

   def __repr__(self):
      return f'<NODE_DATA MASTER: {self.master} ADDR: {self.addr}>'
      
class patroni_tester:
   def __init__(self, host, dbname, user, password, timeout, port, commit):
      self.host = host
      self.dbname = dbname
      self.user = user
      self.password = password
      self.timeout = timeout
      self.port = port
      self.commit = commit

      self.connection_string = f'host={host} port={port} dbname={dbname} user={user} password={password} connect_timeout={timeout}'
      self.logger = setup_logger('PATRONI-HATEST')
      self.logger.info(f'PATRONI TESTER STARTED WITH PARAMS: {self}')

   def __repr__(self):
      return f'<PATRONI_TESTER HOST={self.host} DBNAME={self.dbname} USER={self.user} PASSWORD={self.password} TIMEOUT={self.timeout} PORT={self.port} COMMIT={self.commit}>'

   def connect(self):
      try:
         self.connection = psycopg2.connect(self.connection_string)
         return self
      except psycopg2.Error as e:
         self.logger.error("UNABLE TO CONNECT TO DATABASE", exc_info=True)

   def recognize_host(self):
      try:
         self.connection.cursor.execute("SELECT pg_is_in_recovery(), inet_server_addr()")
         rows = self.connection.cursor.fetchone()
         return node_data(*rows)
      except Exception as e:
         self.logger.error('CANNOT RECOGNIZE NODE ROLE', exc_info=True)

   def process_master(self):
      self.logger.info(f"WORKING WITH MASTER"),
      
      if not self.commit:
         self.logger.info("NO ATTEMPT TO INSERT DATA")
         return
      
      self.connection.cursor.execute("INSERT INTO HATEST VALUES(CURRENT_TIMESTAMP) RETURNING TM")
      if self.connection.cursor.rowcount != 1:
         return
      
      self.connection.commit()
      tmrow = str(self.connection.cursor.fetchone()[0])
      self.logger.info (f'INSERTED: {tmrow}')

   def process_replica(self):
      if not self.commit:
         self.logger.info ('NO ATTEMPT TO RETRIVE DATA')
         return
      
      self.logger.info(f"WORKING WITH REPLICA"),
      self.connection.cursor.execute("SELECT MAX(TM) FROM HATEST")
      row = self.connection.cursor.fetchone()
      self.logger.info(f'RETRIVED: {str(row[0])}')

   def test(self):
      while 1:
         try:
            sleep(1)
            self.connect()
            nd = self.recognize_host()
            self.logger.info(f'WORKING WITH HOST: {nd}')
            if nd.master:
               self.process_master()
            else:
               self.process_replica()
         except Exception as e:
            self.logger.error('ERROR ON TEST PROCESSING', exc_info=True)

@click.command()
@click.option('-h', '--host', type=str, default='127.0.0.1', show_default=True)
@click.option('-d', '--dbname', type=str, default='postgres', show_default=True)
@click.option('-u', '--user', type=str, default='postgres', show_default=True)
@click.option('-p', '--password', type=str)
@click.option('-t', '--timeout', type=int, default=5, show_default=True, help='Connection timeout')
@click.option('-c', '--commit', type=bool, default=False, show_default=True, help='Whether to make changes to the database or not')
@click.argument('port')
def main(host, dbname, user, password, timeout, port, commit):
   return patroni_tester(host, dbname, user, password, timeout, port, commit).test()

if __name__ == "__main__":
   main()

