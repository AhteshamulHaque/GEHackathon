from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..connection import conn_pool

from flask_login import login_user, login_required, logout_user, current_user
from ..model import User

client_auth = Blueprint('client_auth', __name__, url_prefix='/c')

@client_auth.route('/')
def index():
   return redirect( url_for('client_auth.login_page') )


@client_auth.route('/login')
def login_page():
   
   if current_user.is_authenticated:
      return redirect( url_for('client.home') )
   
   return render_template('client/client_login.html', title="Login")


@client_auth.route('/login', methods=['POST'])
def login():
   email = request.form.get('email')
   password = request.form.get('password')
   
   cursor = conn_pool.getCursor()
   
   stmt = cursor.mogrify("SELECT * FROM users WHERE email=%(email)s", {'email': email })
   
   cursor.execute(stmt)
   result = cursor.fetchone()
   
   # check if user actually exists
   # take the user supplied password, hash it, and compare it to the hashed password in database
   if not result or not check_password_hash(result['passwd'], password): 
      flash('Please check your login details and try again.')
      return redirect(url_for('client_auth.login_page')) # if user doesn't exist or password is wrong, reload the page

   user = User( email=email, username=result['username'] )
   login_user(user)
   
   # if the above check passes, then we know the user has the right credentials
   return redirect(url_for('client.home'))


@client_auth.route('/signup')
def signup_page():
   return render_template('client/client_signup.html', title="Sign Up")


@client_auth.route('/signup', methods=['POST'])
def signup():
   # get form data
   email = request.form.get('email')
   username = request.form.get('username')
   password = request.form.get('password')

   # if this returns a user, then the email already exists in database
   # acquire the cursor and conn
   cursor = conn_pool.getCursor()
   
   stmt = cursor.mogrify("SELECT email FROM users WHERE email=%(email)s OR username=%(username)s", {
      'email': email,
      'username': username
   })
   
   cursor.execute(stmt)
   result = cursor.fetchone()

   if result: # if a user is found, we want to redirect back to signup page so user can try again
      flash('Email address or username already exists')
      return redirect(url_for('client_auth.signup_page'))

   # create new user with the form data. Hash the password so plaintext version isn't saved.
   stmt = cursor.mogrify(
      "INSERT INTO users(email, username, passwd) VALUES(%(email)s, %(username)s, %(passwd)s)", {
      'email':email,
      'username': username,
      'passwd': generate_password_hash(password, method='sha256')
   })
   
   cursor.execute(stmt)
   
   user = User(email=email, username=username)
   
   login_user(user)
   
   # release the cursor and conn
   conn_pool.releaseCursor(cursor)

   return redirect(url_for('client.home'))


@client_auth.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('client_auth.login_page'))