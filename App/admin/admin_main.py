from flask import Blueprint, render_template, redirect, url_for, request
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
   stmt = cursor.mogrify("SELECT id, name, description, array_length(assets, 1) as file_count FROM datasets GROUP BY id LIMIT %(limit)s OFFSET %(offset)s", {
      'limit': limit,
      'offset': offset 
   })
   
   print(stmt)
   cursor.execute(stmt)
   # fetch all the datasets
   datasets = cursor.fetchall()
   
   # get the total no. of datasets
   stmt = cursor.mogrify("SELECT COUNT(*) as total FROM datasets ")
   
   print(stmt)
   cursor.execute(stmt)
   
   # fetch the count of the datasets
   total = cursor.fetchone()['total']
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   # fake dataset
   datasets = [{
      'id': hexlify(urandom(15)).decode('utf-8'),
      'name': '2006 De-identification and Smoking Status Challenge Downloads',
      'description': 'The majority of these Clinical Natural Language Processing (NLP) data sets were originally created at a former NIH-funded National Center for Biomedical Computing (NCBC) known as i2b2: Informatics for Integrating Biology and the Bedside.',
      'file_count': 10
   }]
   
   total = 50
   
   return render_template(
      'admin/admin_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total
   )


# route for a particular dataset i.e it shows files
# for a particular dataset using pagination
@admin.route('/dataset/<dset_id>')
@admin_login_required
def dataset_with_id(dset_id):
   
   # show files using pagination
   page = request.args.get('page', 0) # offset for the files in the database
   limit = 20 # no. of dataset
   
   offset = page*limit
   
   # acquire cursor
   cursor = conn_pool.getCursor()
   
   # TODO - get the list of files with their ids
   stmt = cursor.mogrify("SELECT id, name, description, array_length(assets, 1) as file_count FROM datasets LIMIT %(limit)s OFFSET %(offset)s", {
      'limit': limit,
      'offset': offset 
   })
   
   print(stmt)
   cursor.execute(stmt)
   
   # fetch all the datasets
   files = cursor.fetchall()
   
   # get total no of files related to this dataset
   stmt = cursor.mogrify("SELECT COUNT(*) AS total FROM datasets")
   cursor.execute(stmt)
   
   total = cursor.fetchone()['total']
   
   # release cursor which releases the conn
   conn_pool.releaseCursor(cursor)
   
   # fake dataset
   files = [{
      'id': hexlify(urandom(15)).decode('utf-8'),
      'fname': 'Some random file name',
      'mimetype':'image/png',
      'tags': ['disease1', 'disease2', 'disease2']
   }]
   
   return render_template(
      'admin/admin_dataset_files.html', title="Datasets",
      files=files, page=page, total=total
   )
   

# application logic
@admin.route('/applications')
def applications():
   
   return render_template('admin/admin_application.html', title="Application")