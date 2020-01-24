from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .admin_auth import admin_login_required
from ..connection import conn_pool

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
   stmt = cursor.mogrify("SELECT id, name, array_length(assets, 1) as file_count FROM datasets LIMIT %(limit)s OFFSET %(offset)s", {
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
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   # fake dataset
   # datasets = [{
   #    'id': hexlify(urandom(15)).decode('utf-8'),
   #    'name': '2006 De-identification and Smoking Status Challenge Downloads',
   #    'description': 'The majority of these Clinical Natural Language Processing (NLP) data sets were originally created at a former NIH-funded National Center for Biomedical Computing (NCBC) known as i2b2: Informatics for Integrating Biology and the Bedside.',
   #    'file_count': 10
   # }]
   
   # total = 50
   
   return render_template(
      'admin/admin_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total
   )


# route for a particular dataset i.e it shows files
# for a particular dataset using pagination
@admin.route('/datasets/<dset_id>')
@admin_login_required
def dataset_with_id(dset_id):
   
   # show files using pagination
   page = int(request.args.get('page', 0)) # offset for the files in the database
   limit = 20 # no. of dataset

   # pagination is implemented using ARRAY SLICING over assets `datatype` field
   # in `dataset` TABLE   
   start = page*limit
   end = start+limit
   
   # acquire cursor
   cursor = conn_pool.getCursor()

   # due to array slicing problem the below statement is not mogrified
   stmt = "SELECT assets["+str(start)+":"+str(end)+"] FROM datasets WHERE id='%s'"%(dset_id)   
   cursor.execute(stmt)
   
   # the data is returned as [[[id, id, .... ]]] hence the below line
   files_id_array = cursor.fetchone()[0] # here files is an array of ids
   
   # convert files to postgresql array
   files_id_array = str(files_id_array)
   files_id_array = files_id_array.replace('[', '{').replace(']', '}').replace("'", '').replace('"', '') # postgresql array
   
   # get details of individual source files using file_id_array
   stmt = cursor.mogrify("SELECT id, fname, octet_length(asset_data) as size, mimetype FROM s_assets WHERE id=ANY(%s)", (files_id_array,) )
   
   cursor.execute(stmt)
   source_files = cursor.fetchall()
   
   # get details of individual deidentified files using file_id_array
   stmt = cursor.mogrify("SELECT id FROM d_assets WHERE id=ANY(%s)", (files_id_array,) )
   cursor.execute(stmt)
   deientified_files = cursor.fetchall()

   # get total no of files related to this dataset
   stmt = cursor.mogrify("SELECT array_length(assets, 1) AS total FROM datasets WHERE id=%s", (dset_id, ))
   cursor.execute(stmt)
   
   total = cursor.fetchone()['total']
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   # fake dataset
   # files = [{
   #    'id': hexlify(urandom(15)).decode('utf-8'),
   #    'fname': 'Some random file name',
   #    'mimetype':'image/png',
   #    'tags': ['disease1', 'disease2', 'disease2']
   # }]
   
   # dset_id is used for prev and next links
   return render_template(
      'admin/admin_dataset_files.html', title="Datasets Files",
      dset_id=dset_id, source_files=source_files, page=page, total=total,
      deientified_files=deientified_files
   )
   

# this route is downloading a particular file
@admin.route('/file/<file_id>')
@admin_login_required
def delete_particular_file(file_id):
   return "Delete %s"%file_id
   

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