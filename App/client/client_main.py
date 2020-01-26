from flask import (
   Blueprint, render_template, redirect, url_for,
   request, flash, Response, jsonify, send_from_directory
)
from flask_login import login_required, current_user
from ..connection import conn_pool

# test imports
import os
from binascii import hexlify

client = Blueprint('client', __name__, url_prefix='/c/m', template_folder='templates/client')

@client.route('/')
@login_required
def home():
   return render_template('client/client_home.html', title="Home")


# route to see the available datasets with pagination
@client.route('/datasets')
@login_required
def all_datasets():
   
   # show datasets using pagination
   page = int(request.args.get('page', 0)) # offset for the dataset in the database
   limit = 20 # no. of dataset
   
   offset = page*limit
   
   # acquire cursor
   cursor = conn_pool.getCursor()
   
   # get the list of datasets with limit = 20
   stmt = cursor.mogrify("SELECT id, name, filename FROM datasets LIMIT %(limit)s OFFSET %(offset)s", {
      'limit': limit,
      'offset': offset 
   })
   
   cursor.execute(stmt)
   
   # fetch all the datasets
   datasets = cursor.fetchall()
   
   # get the total no. of datasets
   stmt = cursor.mogrify("SELECT COUNT(*) as total FROM datasets")
   cursor.execute(stmt)
   
   # fetch the count of the datasets
   total = cursor.fetchone()['total']
   
   # get the status of various datasets that the user has
   # applied application for
   stmt = cursor.mogrify("SELECT dataset_id, status FROM applications WHERE issuer_email=%s", (current_user.email,))
   cursor.execute(stmt)
   
   # { 'id': 'status1', 'id2': 'status2' }
   dset_status = { result['dataset_id']: result['status'] for result in cursor }
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   return render_template(
      'client/client_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total,
      dset_status=dset_status
   )


# route to download a particular dataset
# this can only be accessed by a client if he/she has the approved application
@client.route('/d/assets/<dset_id>')
@login_required
def dataset_with_id(dset_id):

   # acquire cursor
   cursor = conn_pool.getCursor()

   # check if this user has access to the dataset or not
   stmt = cursor.mogrify("SELECT dataset_id FROM applications WHERE status=%s AND issuer_email=%s AND dataset_id=%s", ('approved', current_user.email, dset_id))
   cursor.execute(stmt)
   access = cursor.fetchone()
   
   if not access:
      
      return Response(
         "You are not authorized to access this dataset",
         status=401,
         content_type="text/plain")
   
   # if client has access
   stmt = cursor.mogrify("SELECT * FROM datasets WHERE id=%s", (dset_id,))
   cursor.execute(stmt)
   dataset = cursor.fetchone()
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)

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
   
   
# client application logic
# this route is used to send request for a dataset
@client.route('/application/<dset_id>', methods=['GET', 'POST'])
@login_required
def application_for_dataset(dset_id):
   
   if request.method == "GET":
      
      # acquire the cursor and connection
      cursor = conn_pool.getCursor()
      
      # select id, name for the dataset and pass
      stmt = cursor.mogrify("SELECT id, name FROM datasets WHERE id=%s", (dset_id,))
      cursor.execute(stmt)
      
      dataset = cursor.fetchone()
      
      # release the cursor and connection
      conn_pool.releaseCursor(cursor)     
      
      return render_template('client/client_apply_application.html', dataset=dataset)
   
   elif request.method == "POST":
      
      title = request.form['title']
      content = request.form['content']
      
      # acquire the cursor and connection
      cursor = conn_pool.getCursor()
      
      # submit the application for further processing
      app_id = hexlify( os.urandom(15) ).decode('utf-8')

      # initially the application is submitted for processing
      stmt = cursor.mogrify('''INSERT INTO applications(id, title, content, status, issuer_email, dataset_id)
         VALUES(%s, %s, %s, %s, %s, %s)''', (
            app_id, title, content, 'processing', current_user.email, dset_id
         ))
      cursor.execute(stmt)
            
      # release the cursor and connection
      conn_pool.releaseCursor(cursor)
      
      flash('Your application submitted successfully')
      return redirect( url_for('client.application_for_dataset', dset_id=dset_id) )
   

@client.route('/application')
@login_required
def application():
   
   cursor = conn_pool.getCursor()
   
   stmt = cursor.mogrify("SELECT * FROM applications WHERE issuer_email=%s", (current_user.email,) )
   cursor.execute(stmt)
   
   applications = cursor.fetchall()
   
   conn_pool.releaseCursor(cursor)
   
   return render_template('client/client_application.html',
      title="My Applications", applications=applications)