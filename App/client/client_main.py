from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
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
   
   # get the status of various datasets that the user has
   # applied application for
   stmt = cursor.mogrify("SELECT dataset_id, status FROM applications WHERE issuer_email=%s", (current_user.email,))
   cursor.execute(stmt)
   
   # { 'id': 'staus', 'id2': 'statu2' }
   dset_status = { result['dataset_id']: result['status'] for result in cursor }
   
   print(dset_status)
   
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
      'client/client_dataset.html', title="Datasets",
      datasets=datasets, page=page, total=total,
      dset_status=dset_status
   )


# route for a particular dataset i.e it shows files
# for a particular dataset using pagination
# this can only be accessed by a client if he/she has the approved application
@client.route('/dataset/<dset_id>')
@login_required
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
   
   # get details of individual deidentified files using `file_id_array`
   stmt = cursor.mogrify("SELECT id FROM d_assets WHERE id=ANY(%s)", (files_id_array,) )
   cursor.execute(stmt)
   deientified_files = cursor.fetchall()

   # get total no of files related to this dataset
   stmt = cursor.mogrify("SELECT array_length(assets, 1) AS total FROM datasets WHERE id=%s", (dset_id, ))
   cursor.execute(stmt)
   
   total = cursor.fetchone()['total']
   
   # release cursor which releases the conn                {{ dset_status.keys() }}
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
      'client/client_dataset_files.html', title="Datasets Files",
      dset_id=dset_id, source_files=source_files, page=page, total=total,
      deientified_files=deientified_files
   )


@client.route('/files/<file_id>')
@login_required
def get_particular_file(file_id):
   
   cursor = conn_pool.getCursor()
   
   # get file and its meta content using `s_assets` and `d_assets` TABLE
   stmt = cursor.mogrify("SELECT fname, d_assets.asset_data, mimetype FROM s_assets INNER JOIN d_assets ON d_assets.id = s_assets.id WHERE d_assets.id = %s", (file_id,))
   cursor.execute(stmt)
   file = cursor.fetchone()
   
   # file[0] = fname, file[1] = <memory file>, file[2] = mimetype
   
   conn_pool.releaseCursor(cursor)
   
   return Response(
        file[1],
        mimetype=file[2],
        headers={"Content-disposition":
                 "attachment; filename={}".format(file[0]) })
   
   
   
# client application logic
# this route is used to send request for a dataset
@client.route('/application/<dset_id>', methods=['GET', 'POST'])
@login_required
def application_for_dataset(dset_id):
   
   if request.method == "GET":
      
      # acquire the cursor and connection
      cursor = conn_pool.getCursor()
      
      # select id, name, description for the dataset and pass
      stmt = cursor.mogrify("SELECT id, name FROM datasets WHERE id=%s", (dset_id,))
      cursor.execute(stmt)
      
      dataset = cursor.fetchone()
      
      # release the cursor and connection
      conn_pool.releaseCursor(cursor)     
      
      # test data
      # dataset = {
      #    'id': hexlify(urandom(15)).decode('utf-8'),
      #    'name': 'Some random name',
      #    'description': 'A random long description for the dataset'
      # }
      
      return render_template('client/client_apply_application.html', dataset=dataset)
   
   elif request.method == "POST":
      
      title = request.form['title']
      content = request.form['content']
      
      # acquire the cursor and connection
      cursor = conn_pool.getCursor()
      
      # submit the application for further processing
      app_id = hexlify( urandom(15) ).decode('utf-8')

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