from flask import (
   Blueprint, render_template, redirect, url_for, request,
   flash, session
)

from werkzeug.security import generate_password_hash, check_password_hash
from ..connection import conn_pool
from functools import wraps

admin_auth = Blueprint('admin_auth', __name__, url_prefix='/a')


# admin login required implementation
def admin_login_required(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if 'admin' in session:
         return f(*args, **kwargs)
      else:
         return redirect(url_for('admin_auth.login'))

   return wrap

#************************** ADMIN: LOGIN, SIGN UP, LOGOUT CODE ************************

@admin_auth.route('/')
def index():
   return redirect( url_for('admin_auth.login_page') )

@admin_auth.route('/login')
def login_page():
   
   if session.get('admin', False):
      return redirect( url_for('admin.home') )
   
   return render_template('admin/admin_login.html')


@admin_auth.route('/login', methods=['POST'])
def login():
   username = request.form.get('username')
   password = request.form.get('password')
   
   cursor = conn_pool.getCursor()
   
   stmt = cursor.mogrify("SELECT * FROM admin WHERE username=%(username)s", {
      'username': username
   })
   print(stmt)
   
   cursor.execute(stmt)
   result = cursor.fetchone()

   # check if user actually exists
   # take the user supplied password, hash it, and compare it to the hashed password in database
   if not result or not check_password_hash(result['passwd'], password): 
      flash('Please check your login details and try again.')
      return redirect(url_for('admin_auth.login')) # if user doesn't exist or password is wrong, reload the page
   
   # login the admin
   session['username'] = result['username']
   session['admin'] = True
   
   # if the above check passes, then we know the user has the right credentials
   return redirect(url_for('admin.home'))


@admin_auth.route('/signup')
def signup_page():
   return render_template('admin/admin_signup.html', title="Sign Up")


@admin_auth.route('/signup', methods=['POST'])
def signup():
   # get form data
   username = request.form.get('username')
   password = request.form.get('password')

   # if this returns a user, then the email already exists in database
   # acquire the cursor and conn
   cursor = conn_pool.getCursor()
   
   stmt = cursor.mogrify("SELECT username FROM admin WHERE username=%(username)s", {
      'username': username
   })
   print(stmt)
   
   cursor.execute(stmt)
   admin = cursor.fetchone()

   if admin: # if a user is found, we want to redirect back to signup page so user can try again
      flash('Email address already exists')
      return redirect(url_for('admin_auth.signup_page'))

   # create new user with the form data. Hash the password so plaintext version isn't saved.
   stmt = cursor.mogrify(
      "INSERT INTO admin(username, passwd) VALUES(%(username)s, %(passwd)s)", {
      'username': username,
      'passwd': generate_password_hash(password, method='sha256')
   })
   print(stmt)
   
   cursor.execute(stmt)
   
   # login the admin
   session['username'] = username
   session['admin'] = True
   
   # release the cursor and conn
   conn_pool.releaseCursor(cursor)

   return redirect(url_for('admin.home'))


@admin_auth.route('/logout')
@admin_login_required
def logout():
   session.pop('username')
   session.pop('admin')
   return redirect(url_for('admin.home'))