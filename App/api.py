from flask import Blueprint, jsonify, make_response
from flask_restful import reqparse
import werkzeug
from flask_sqlalchemy import SQLAlchemy
from os import urandom
from binascii import hexlify
from random import randint, choice
from string import ascii_lowercase, ascii_uppercase, digits

api = Blueprint('api', __name__, url_prefix='/api')

from app import db
from dbmodel import File

from ml_and_regex.deidentifier import master

# Random filename generator
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


@api.route("/deidentify", methods=["POST"])
def deidentification():

   parser = reqparse.RequestParser()
   parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)
   parser.add_argument('choice', type=int, location='form', default=2)
   
   args = parser.parse_args()
   
   # ***** file content to be deidentified ******
   file_content = args['file'].stream.read().decode('utf-8')

   # TODO - implement the ML model here
   
   final_str, _, _ = master(file_content, args['choice'])
   
   # generate key for the file
   _key = hexlify(urandom(32)).decode('utf-8')
   
   # generate a random filename
   _filename = generate_random_filename()
   
   # save deidentified files
   with open("deidentified_files/"+_filename, "w") as fp:
      fp.write(final_str)
   
   # save source files
   with open("source_files/"+_filename, "w") as fp:
      fp.write(file_content)
            
   # save in the database
   file = File(key=_key, filename=_filename)

   db.session.add(file)
   db.session.commit()      
   
   return jsonify(key=_key, file=final_str)
      

@api.route("/reidentify", methods=["POST"])
def reidentification():
   
   parser = reqparse.RequestParser()
   parser.add_argument('key', location='form', required=True)
   # parser.add_argument('identify', type=str, location='form') # recieved as as comma seperated values
   
   args = parser.parse_args()
   
   # select proper from database and build a dictionary for the ML model      
   # _dict = {}
   
   # check if it is a valid key by getting the filename
   file = File.query.filter_by(key=args['key']).first()
   
   if file:         
      
      with open("source_files/"+file.filename) as fp:
         file_content = fp.read()
            
      return jsonify(file=file_content)
   
   else:
      response = make_response(jsonify(error='Invalid Key'), 422)
      return response