# GEHackathon

## Quick Start
This project contains two separated folders(not related to one another):

- [Frontend](https://github.com/AhteshamulHaque/GEHackathon/Frontend) - which uses Angular to create interactive webpage.  
- [App](https://github.com/AhteshamulHaque/GEHackathon/Backend) - which has **Flask API**, **ML models** and **templates** which constitutes the app. 

## Installation

**NOTE:** You'll need to use python3. Using venv(virtual environment) is recommended.

Clone and setup a virtual environment:
   
    git clone https://github.com/AhteshamulHaque/GEHackathon.git
    cd GEHackathon/App

Install dependencies:

    pip3 install --upgrade pip
    pip3 install -r requirements.txt

## App
 **File Structure**
  ```
  |-- MLmodels/            # Contains all the trained models for ML
  |      |-- ....
  |      |-- ....
  |-- templates/	   # html files
  |-- static/		   # js, css, images, favicons, etc
  |-- files/		   # contains the DEIDENTIFIED files
  |-- app.py               # main app
  |-- api.py               # api routes to handle requests. Implement ML models here
  |-- dbmodel.py           # database structure/model
  |-- requirements.txt
  |-- database.db          # database file ( this is created automatically )
  ```
 
 Accepts the two important request:
 **POST** -> http://localhost:5000/deidentify: (Deidentifies data)
  ```
    Request:
    {
      file: '@filename' // @filename is the name of the file to be deidentified
    }
    
    Response:
    {
      key: 'random_key_value' // required to reidentify parts of the deidentified file (eg: date, name, etc)
    }
  ```
  
  **POST** -> http://localhost:5000/reidentify: (Reidentifies data)
  ```
    Request:
    {
      key: 'random_key_value' // key for reidentification
      identify: ['date', 'name', 'adhar', .... ] // (optional) tells which parts to identify
    }
    
    Response:
    {
      file: 'file_contents' // reidentified file
    }
  ```

