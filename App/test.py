from flask import Blueprint, redirect, url_for
from .connection import conn_pool
import os, shutil
from binascii import hexlify
from .connection import conn_pool

test = Blueprint('test', __name__, url_prefix='/t')

@test.route('/')
def index():
   return redirect( url_for('test.create_database') )


@test.route('/createdb')
def create_database():
   
   try:
      # remove the deidentified_assets tree
      shutil.rmtree('deidentified_assets')
   except:
      pass
   finally:
      #copy all the files from source_assets to deidentified_assets
      shutil.copytree('source_assets', 'deidentified_assets')
   
   datasets = [
      '2006 De-identification and Smoking Status Challenge Downloads',
      'Test Data: Ground Truth for Intuitive Judgments on Test Data',
      '2014 De-identification and Heart Disease Risk Factors Challenge Downloads'
   ]
   
   zipfiles = os.listdir('source_assets')
   
   # acquire the cursor and connection
   cursor = conn_pool.getCursor()
   
   for zip_filename, dset_name in zip(zipfiles, datasets):
   
      # generate a random key for the dataset
      dset_id = hexlify(os.urandom(15)).decode('utf-8')
      
      # create an entry for `dset_name` dataset
      stmt = cursor.mogrify("INSERT INTO datasets VALUES(%(id)s, %(name)s, %(filename)s, %(status)s)", {
         'id': dset_id,
         'name': dset_name,
         'filename': zip_filename,
         'status': 1
      })
      cursor.execute(stmt)
      
   # release the cursor and conn
   conn_pool.releaseCursor(cursor)
   
   return "Database created"