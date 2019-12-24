from flask import Flask, render_template
from os import urandom
from flask_sqlalchemy import SQLAlchemy
from binascii import hexlify
from api import api

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = hexlify(urandom(23))

db = SQLAlchemy(app)
app.register_blueprint(api)

@app.route("/")
def index():
   return render_template("index.html", title="GE Hackathon")
      

if __name__ == "__main__":
   app.run(debug=True)