from flask import Blueprint, jsonify, make_response
from flask_restful import reqparse
import werkzeug
from flask_sqlalchemy import SQLAlchemy
from os import urandom
from binascii import hexlify
from random import randint

api = Blueprint('api', __name__, url_prefix='/api')

from app import db
from dbmodel import File, Date, PersonName, DrivingLicense, AdharCard

# TODO - Import the ML model here

@api.route("/deidentify", methods=["POST"])
def deidentification():

   parser = reqparse.RequestParser()
   parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)
   args = parser.parse_args()
   
   # ***** file content to be deidentified ******
   file_content = args['file'].stream.read().decode('utf-8')
   
   # ***** will contain all deidentified data ******
   _dict = {}
   
   # TODO - implement the ML model here
   
   # TODO - generate a list of identified data in a dictionary (eg: date, name, etc)
   
   # generate key for the file
   _key = hexlify(urandom(32)).decode('utf-8')
   
   # generate a random filename
   _filename = hexlify(urandom(10)).decode('utf-8') + args['file'].name
   
   with open("files/"+_filename, "w") as fp:
      fp.write(file_content)
      
   # save in the database
   file = File(key=_key, filename=_filename)
   
   date = Date(date='12/12/2028', start_index=randint(1, 100), end_index=randint(1, 100), key_id=file.key)
   person = PersonName(name='NileKrator', start_index=randint(1, 100), end_index=randint(1, 100), key_id=file.key)
   license = DrivingLicense(license_no='2342DIOIS', start_index=randint(1, 100), end_index=randint(1, 100), key_id=file.key)
   adharCard = AdharCard(adhar_no='34234234234', start_index=randint(1, 100), end_index=randint(1, 100), key_id=file.key)
   
   db.session.add(file)
   db.session.add(date)
   db.session.add(person)
   db.session.add(license)
   db.session.add(adharCard)
   
   db.session.commit()      
   
   return jsonify(key=_key, file=file_content)
      

@api.route("/reidentify", methods=["POST"])
def reidentification():
   
   parser = reqparse.RequestParser()
   parser.add_argument('key', location='form', required=True)
   parser.add_argument('identify', type=str, location='form') # recieved as as comma seperated values
   
   args = parser.parse_args()
   
   # select proper from database and build a dictionary for the ML model      
   _dict = {}
   
   # check if it is a valid key by getting the filename
   filename = File.query.filter(File.key==args['key'])
   
   if filename:
      
      # get dates from database
      dates = []
      result = Date.query.filter(Date.key_id==args['key'])
      for res in result:
         dates.append([res.date, res.start_index, res.end_index])
         
      _dict['dates'] = dates
      
      # get person names from database
      names = []
      result = PersonName.query.filter(PersonName.key_id==args['key'])
      for res in result:
         names.append([res.name, res.start_index, res.end_index])
      
      _dict['names'] = names
      
      # get license no from database
      license = []
      result = DrivingLicense.query.filter(DrivingLicense.key_id==args['key'])
      for res in result:
         license.append([res.license_no, res.start_index, res.end_index])
      
      _dict['license'] = license
      
      # get adhar card no from database
      adhar_card = []
      result = AdharCard.query.filter(AdharCard.key_id==args['key'])
      for res in result:
         adhar_card.append([res.adhar_no, res.start_index, res.end_index])
         
      _dict['adhar_card'] = adhar_card
      
      # TODO - pass the dictionary to reidentify using ML model
               
      return jsonify(file='Reidentified file content')
   
   else:
      response = make_response(jsonify(error='Invalid Key'), 422)
      return response