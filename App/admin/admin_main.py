from flask import (
   Blueprint, render_template, redirect, url_for, request,
   flash, Response
)
from threading import Thread
import base64, os, time, mimetypes
from werkzeug import secure_filename

# app imports
from admin.admin_auth import admin_login_required
from connection import conn_pool

# deidentification tool import
from deidentifier.deidentify_main import deidentify_zipfile

# imported for testing purpose
from os import urandom
from binascii import hexlify

admin = Blueprint('admin', __name__, url_prefix='/a/m')

@admin.route('/')
@admin_login_required
def home():
   return render_template('admin/admin_home.html', title="Home")


# route to see the available datasets with pagination
@admin.route('/datasets')
@admin_login_required
def all_datasets():
   # show datasets using pagination
   page = int(request.args.get('page', 0)) # offset for the dataset in the database
   limit = 20 # no. of dataset
   
   offset = page*limit
   
   # acquire cursor
   cursor = conn_pool.getCursor()
   
   # get the list of datasets with limit = 20
   stmt = cursor.mogrify("SELECT * FROM admin_datasets LIMIT %(limit)s OFFSET %(offset)s", {
      'limit': limit,
      'offset': offset
   })
   
   cursor.execute(stmt)
   
   # fetch all the datasets
   datasets = cursor.fetchall()
   
   # get the total no. of datasets
   stmt = cursor.mogrify("SELECT COUNT(*) as total FROM admin_datasets")
   cursor.execute(stmt)
   
   # fetch the count of the datasets
   total = cursor.fetchone()['total']
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   return render_template(
      'admin/admin_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total
   )


# route for a particular dataset i.e it shows files
# for a particular dataset using pagination
# TODO - needs to be modified
@admin.route('/datasets/<asset_type>/<dset_id>')
@admin_login_required
def dataset_with_id(asset_type, dset_id):
   
   # `asset type` defines if the document is source or deidentified
   # acquire cursor
   cursor = conn_pool.getCursor()
   
   # get dataset metadata
   stmt = cursor.mogrify("SELECT * FROM datasets WHERE id=%s", (dset_id,))
   cursor.execute(stmt)
   dataset = cursor.fetchone()
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)

   if asset_type == 'src':
      filepath = os.path.join('source_assets', dataset['filename'])
   else:
      filepath = os.path.join('deidentified_assets', dataset['filename'])
   
   
   # send the zip file
   return Response(
      open(filepath, 'rb'),
      headers={
         "Pragma": "public",
         "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
         "Cache-Control": "public",
         "Content-Description": "File Transfer",
         "Content-type": "application/octet-stream",
         "Content-Transfer-Encoding": "binary",
         # "Content-Length: ".filesize($filepath.$filename)),
         "Content-Disposition": "attachment; filename=%s;" % dataset['filename']
      }
   )
   

# application logic
@admin.route('/applications', methods=['GET', 'POST'])
@admin_login_required
def applications():
   
   # acquire the connection and cursor
   cursor = conn_pool.getCursor()
   
   if request.method == "GET":
      
      # get all the applications
      stmt = cursor.mogrify("SELECT id, title, content, status, issuer_email, dataset_id FROM applications WHERE status='processing'")
      cursor.execute(stmt)
      applications = cursor.fetchall()
      
      # release the cursor and connection
      conn_pool.releaseCursor(cursor) 
        
      return render_template('admin/admin_application.html',
         title="Application", applications=applications)
   
   elif request.method == "POST":
      
      # get the issuer_id
      issuer_email = request.form.get('issuer_email')
      # get the dataset_id
      dset_id = request.form.get('dset_id')
      
      # this means approve button is clicked
      if request.form.get('approve') != None:
         stmt = cursor.mogrify("UPDATE applications SET status=%s WHERE issuer_email=%s AND dataset_id=%s", ('approved', issuer_email, dset_id))
         msg = 'Application is approved successfully'
         
      # this means reject button is clicked
      elif request.form.get('reject') != None:
         stmt = cursor.mogrify("UPDATE applications SET status=%s WHERE issuer_email=%s AND dataset_id=%s", ('rejected', issuer_email, dset_id))
         msg = 'Application rejected successfully'
         
      cursor.execute(stmt)
      # release the connection
      conn_pool.releaseCursor(cursor)
      flash(msg)
      
      return redirect( url_for('admin.applications') )
   

# route to check single deidentification by the admin
@admin.route('/single', methods=['GET', 'POST'])
@admin_login_required
def single_deidentification():
   
   if request.method == 'GET':
      return render_template('admin/deidentify.html', title="Deidentify")
   
   
   elif request.method == 'POST':
      
      file = request.files['src_file']
      mime = mimetypes.MimeTypes()
      
      mimetype = mime.guess_type(file.filename)[0]
      
      # deidentify according to filetype
      if 'image' in mimetype:
         print("image passed")
         result = f'data:{mimetype};base64,'
         
         result += (base64.b64encode( file.stream.read() )).decode('utf-8')
         
         print(result[:40])
      elif 'audio' in mimetype:
         print("audio passed")
         result = "Some text"
      else:
         print("text passed")
         result = file.stream.read().decode('utf-8')
      
      return render_template('admin/deidentify.html',
         title="Deidentify", result=result, mimetype=mimetype)
      
      

# upload logic for admin datasets upload
@admin.route('/upload', methods=['POST'])
@admin_login_required
def upload():
   
   # get the file from the form
   file = request.files['zipfile']
   
   # generating filepath
   # gives unidentified error while saving by any other way
   src_zip_path = os.path.join('source_assets', secure_filename(file.filename))
   dest_zip_path = os.path.join('deidentified_assets', secure_filename(file.filename))
   
   # save the files in source_assets
   file.save( src_zip_path )
   
   # acquire the cursor and connection
   cursor = conn_pool.getCursor()  
   
   # generate a file id
   zip_info = {
      'id': hexlify(os.urandom(15)).decode('utf-8'),
      'name': request.form['dataset_name'],
      'filename': file.filename,
      'src_zip_path': src_zip_path,
      'dest_zip_path': dest_zip_path,
      'status': 0
   }
   
   # insert processing entry for the dataset_asset
   stmt = cursor.mogrify("INSERT INTO admin_datasets VALUES(%(id)s, %(name)s, %(filename)s, %(status)s)", zip_info)

   print(stmt)
   cursor.execute(stmt)
   
   # schedule the deidentification of data
   th = Thread( target=deidentify_datasets, args=(zip_info,) )
   th.start()
   
   # release the cursor and connection
   conn_pool.releaseCursor(cursor)
   
   return redirect( url_for('admin.all_datasets') )


def deidentify_datasets(zip_info):
   
   # ...... deidentification in progress
   # after successfull deidentification it saves the deidentified files also
   # this will be done automatically after deidentification
   file_count = deidentify_zipfile(zip_info['src_zip_path'], zip_info['dest_zip_path'] )
   
   # acquire the cursor and connection
   cursor = conn_pool.getCursor()
   
   # update the datasets for the admin
   stmt = cursor.mogrify("UPDATE admin_datasets SET upload_status=%(status)s WHERE id=%(id)s", {
      'id': zip_info['id'],
      'status': 1
   })
   cursor.execute(stmt)
   
   # update filecount for the admin
   stmt = cursor.mogrify("UPDATE admin_datasets SET filecount=%(filecount)s  WHERE id=%(id)s", {
      'id': zip_info['id'],
      'filecount': file_count
   })
   cursor.execute(stmt)
   
   # insert the datasets for the client
   stmt = cursor.mogrify("INSERT INTO datasets VALUES(%(id)s, %(name)s, %(filename)s, %(filecount)s)", {
      'id': zip_info['id'],
      'name': zip_info['name'],
      'filename': zip_info['filename'],
      'filecount': file_count
   })
   cursor.execute(stmt)
   
   # release the cursor and connection
   conn_pool.releaseCursor(cursor)