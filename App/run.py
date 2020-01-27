from flask import Flask, redirect, url_for
from flask_login import LoginManager
from functools import wraps

def create_app():
   app = Flask(__name__)

   app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

   login_manager = LoginManager()
   login_manager.login_view = 'client_auth.login_page'
   login_manager.init_app(app)

   from model import User

   @login_manager.user_loader
   def load_user(email):
      # since the user_id is just the primary key of our user table, use it in the query for the user
      return User.get(email)
		
   # blueprint for admin auth routes
   from admin.admin_auth import admin_auth as admin_auth_blueprint
   app.register_blueprint(admin_auth_blueprint)
   
   # blueprint for admin main routes
   from admin.admin_main import admin as admin_blueprint
   app.register_blueprint(admin_blueprint)

   # blueprint for client auth routes
   from client.client_auth import client_auth as client_auth_blueprint
   app.register_blueprint(client_auth_blueprint)

   # blueprint for client main routes
   from client.client_main import client as client_blueprint
   app.register_blueprint(client_blueprint)
   
   # blueprint for test routes
   from test import test as test_blueprint
   app.register_blueprint(test_blueprint)
   
   @app.route('/')
   def index():
      return redirect( url_for('client_auth.login') )
   
   return app