import psycopg2
from psycopg2 import pool
from  psycopg2.extras import DictCursor

from random import randint, choice
from string import ascii_lowercase, ascii_uppercase, digits

class ConnectionPool:
   
   def __init__(self):
      # create a threaded poll to use across the app
      self.threaded_pool = psycopg2.pool.ThreadedConnectionPool(
         5, 20,user = "root",
         password = "root",
         host = "localhost",
         port = "5432",
         database = "gehackathon"
      )
      
      self.active_connections = {}
      
   
   def getCursor(self):
      '''
         Creates a connection and stores it in a dictionary
         and return the corresponding cursor
      '''
      ps_connection = self.threaded_pool.getconn()
      
      if(ps_connection):
         
         ps_cursor = ps_connection.cursor(cursor_factory=DictCursor)
         
         # save the mapping `cursor -> connection` in dictionary
         self.active_connections[ps_cursor] = ps_connection
         
         return ps_cursor
   
      return None
   
   def releaseCursor(self, ps_cursor):
      ''' Releases the connection associated with a cursor '''
      ps_cursor.close()

      # get corresponding conn object
      conn = self.active_connections[ps_cursor]

      # commit any related connections
      conn.commit()
      
      # put the connection back to the threaded pool
      self.threaded_pool.putconn(conn)

      # del the connection from the active connections
      del self.active_connections[ps_cursor]

      return True
   
   @staticmethod
   def generate_random_filename():
      '''
         Generates a filename of length between 10 to 15 using alphabets and digits
         Eg: ab48d334fsdf.txt, AB534cdiD0w9df.txt
      '''
   
      filename_length = randint(10, 15)
      chars = [ascii_lowercase, ascii_uppercase, digits]
      
      filename = ''
      for _ in range(filename_length):
      
         random_char = choice( choice(chars) )
         filename += random_char
      
      filename += '.txt'
      
      return filename
   

conn_pool = ConnectionPool()