from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from ..connection import conn_pool

# test imports
from os import urandom
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
      'client/client_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total
   )


# route for a particular dataset i.e it shows files
# for a particular dataset using pagination
@client.route('/dataset/<dset_id>')
@login_required
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
      'client/client_dataset_files.html', title="Datasets",
      files=files, page=page, total=total
   )


# client application logic
@client.route('/application/<dset_id>', methods=['GET', 'POST'])
@login_required
def application_for_dataset(dset_id):
   
   if request.method == "GET":
      
      # acquire the cursor and connection
      cursor = conn_pool.getCursor()
      
      # select id, name, description for the dataset and pass
      stmt = cursor.mogrify("SELECT id, name, description FROM datasets WHERE id=%s", (dset_id))
      cursor.execute(stmt)
      
      dataset = cursor.fetchone()
      
      # release the cursor and connection
      conn_pool.releaseCursor(cursor)     
      
      # test data
      dataset = {
         'id': hexlify(os.urandom(15)).decode('utf-8'),
         'name': 'Some random name',
         'description': 'A random long description for the dataset'
      }
      
      return render_template('client/client_application.html', dataset=dataset)
   
   elif request.method == "POST":
      flash('Your application submitted successfully')
      return redirect( url_for('client.application_for_dataset') )