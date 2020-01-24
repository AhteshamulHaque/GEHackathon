from flask import Blueprint, redirect, url_for
from .connection import conn_pool
import os
from binascii import hexlify
from random import choice
from .connection import conn_pool
import magic

test = Blueprint('test', __name__, url_prefix='/t')

@test.route('/')
def index():
   return redirect( url_for('test.create_database') )


@test.route('/createdb')
def create_database():
   
   datasets = [
      '2006 De-identification and Smoking Status Challenge Downloads',
      'Test Data: Ground Truth for Intuitive Judgments on Test Data',
      '2014 De-identification and Heart Disease Risk Factors Challenge Downloads',
      'Test Data: PHI Set no Tags',
      'Documentation: Track1: De-identification Annotation Task sample data',
   ]
   
   # get path of images
   images = [ 
      os.path.join( os.path.abspath('.'), 'test_assets/images', _) for _ in os.listdir('test_assets/images')
   ]

   # get path of files
   files = [
      os.path.join( os.path.abspath('.'), 'test_assets/files', _) for _ in os.listdir('test_assets/files')
   ]
   
   # get path of audio
   audios = [
      os.path.join( os.path.abspath('.'), 'test_assets/audios', _) for _ in os.listdir('test_assets/audios')
   ]
   
   # limits the no of files in a dataset
   limit = 4
   
   # acquire the cursor and connection
   cursor = conn_pool.getCursor()
   
   # get mime-type of the file
   mime = magic.Magic(mime=True)
   
   for dset_name in datasets:
      
      # generate a random key for the dataset
      dset_id = hexlify(os.urandom(15)).decode('utf-8')
      
      # create an entry for `dset_name` dataset
      stmt = cursor.mogrify("INSERT INTO datasets(id, name) VALUES(%(dset_id)s, %(dset_name)s)", {
         'dset_id': dset_id,
         'dset_name': dset_name
      })
      cursor.execute(stmt)
      
      for _ in range(limit):
         
         ############################## IMG OPERATION ###############################
         # Grab a random image and remove it from the list of images
         img_id = hexlify(os.urandom(15)).decode('utf-8')
         img = choice(images)
         images.remove( images[ images.index(img) ] )
         
         # get mimetype of the image file
         img_mimetype = mime.from_file(img)
         
         # insert the image to `s_assets` TABLE
         stmt = cursor.mogrify("INSERT INTO s_assets (id, fname, asset_data, mimetype) VALUES(%(id)s, %(fname)s, %(asset_data)s, %(mimetype)s)", {
            'id':img_id,
            'fname':img.split('/')[-1],
            'asset_data': open(img,'rb').read(),
            'mimetype': img_mimetype
         })
         cursor.execute(stmt)
         
         # insert the image to `d_assets` TABLE
         stmt = cursor.mogrify("INSERT INTO d_assets (id, asset_data) VALUES(%(id)s, %(asset_data)s)", {
            'id':img_id,
            'asset_data': open(img,'rb').read()
         })
         cursor.execute(stmt)
         
         ############################ FILE OPERATION ##########################
         # Grab a random file and remove it from the list of files
         file_id = hexlify(os.urandom(15)).decode('utf-8')
         file = choice(files)
         files.remove( files[ files.index(file) ] )
         
         # insert the file to `s_assets` TABLE
         # get mimetype of the file
         file_mimetype = mime.from_file(file)
         
         stmt = cursor.mogrify("INSERT INTO s_assets (id, fname, asset_data, mimetype) VALUES(%(id)s, %(fname)s, %(asset_data)s, %(mimetype)s)", {
            'id':file_id,
            'fname':file.split('/')[-1],
            'asset_data': open(file,'rb').read(),
            'mimetype': file_mimetype
         })
         cursor.execute(stmt)
         
         stmt = cursor.mogrify("INSERT INTO d_assets (id, asset_data) VALUES(%(id)s, %(asset_data)s)", {
            'id':file_id,
            'asset_data': open(file,'rb').read()
         })
         cursor.execute(stmt)
         
         ############################### AUDIO OPERATION #############################
         # Grab a random audio and remove it from the list of audios
         audio_id = hexlify(os.urandom(15)).decode('utf-8')
         audio = choice(audios)
         audios.remove( audios[ audios.index(audio) ] )
         
         # insert the audio to `s_assets` TABLE
         # get mimetype of the audio
         audio_mimetype = mime.from_file(audio)
         
         stmt = cursor.mogrify("INSERT INTO s_assets (id, fname, asset_data, mimetype) VALUES(%(id)s, %(fname)s, %(asset_data)s, %(mimetype)s)", {
            'id':audio_id,
            'fname':audio.split('/')[-1],
            'asset_data': open(audio,'rb').read(),
            'mimetype': audio_mimetype
         })
         cursor.execute(stmt)
         
         stmt = cursor.mogrify("INSERT INTO d_assets (id, asset_data) VALUES(%(id)s, %(asset_data)s)", {
            'id':audio_id,
            'asset_data': open(audio,'rb').read()
         })
         cursor.execute(stmt)
         
         ########################### DATASET OPERATION ##############################
         # insert the ids of image, file, audio pointing to the `dset_name` dataset
         stmt = cursor.mogrify("UPDATE datasets SET assets = array_append(assets, %(img_id)s) WHERE id=%(dset_id)s", {
            'dset_id': dset_id,
            'img_id': img_id
         })
         cursor.execute(stmt)
         
                  # insert the ids of image, file, audio pointing to the `dset_name` dataset
         stmt = cursor.mogrify("UPDATE datasets SET assets = array_append(assets, %(file_id)s) WHERE id=%(dset_id)s", {
            'dset_id': dset_id,
            'file_id': file_id
         })
         cursor.execute(stmt)
         
                  # insert the ids of image, file, audio pointing to the `dset_name` dataset
         stmt = cursor.mogrify("UPDATE datasets SET assets = array_append(assets, %(audio_id)s) WHERE id=%(dset_id)s", {
            'dset_id': dset_id,
            'audio_id': audio_id
         })
         cursor.execute(stmt)
         

   # release the cursor and conn
   conn_pool.releaseCursor(cursor)
   
   return "Database created"