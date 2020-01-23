from .connection import conn_pool
from flask_login import UserMixin

#***************************** USER CLASS *******************************
class User(UserMixin):
   
   def __init__(self, **data):
      self.email = data['email']
      self.username = data['username']   
   
   def get_id(self):
      ''' This function is called by user loader. Hence mandatory'''
      return self.email
   
   @classmethod
   def get(cls, email):
      '''
         This is a class function which returns the user from the database
         if present
      '''
      cursor = conn_pool.getCursor()
      
      # try to get a client
      stmt = cursor.mogrify("SELECT email, username FROM users WHERE email=%(email)s", { 'email': email })
      cursor.execute(stmt)
      user = cursor.fetchone()   
      
      conn_pool.releaseCursor(cursor)
      
      if user:
         return cls(**user)
      else:
         return None