-- CONNECT TO POSTGRES
-- sudo -u postgres psql

-- RUN THE BELOW COMMAND TO EXECUTE THIS SQL SCRIPT
-- psql --host=localhost --port=5432 -U root --dbname=gehackathon
   --echo-errors --file="../Projects/GEHackathon/schema.sql" --no-password 

-- NOTE: All BYTEA data insert and delete must be done in binary mode
-- CONNECT TO DATABASE
\c gehackathon;

-- CREATE TABLE `users`
CREATE TABLE IF NOT EXISTS users (
   email VARCHAR(30) PRIMARY KEY NOT NULL,
   username VARCHAR(20) NOT NULL UNIQUE,
   passwd VARCHAR(100)
);

-- INSERT AN DEFAULT USER with password nile
INSERT INTO users VALUES('example@gmail.com', 'test_user', 'sha256$HWi4ve2L$de69136fddcf73c77832ec5eb76b0cbf7b3cd2792171e0be9cf2cbd1d5dacf86');

-- CREATE TABLE `admin`
CREATE TABLE IF NOT EXISTS admin (
   username VARCHAR(20) PRIMARY KEY NOT NULL,
   passwd VARCHAR(100)
);

-- INSERT AN DEFAULT ADMIN with password admin
INSERT INTO admin VALUES('admin', 'sha256$ptkuwZEr$7ecee462fc41eeafdc1459fc0e62987624b2932afecfaab455e67573c2aea07d');

-- datasets accessed by a client
CREATE TABLE IF NOT EXISTS datasets (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   name TEXT,
   filename TEXT
);

-- dataset from which admin reads
CREATE TABLE IF NOT EXISTS admin_datasets (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   name TEXT,
   filename TEXT,
   upload_status INTEGER
);

-- CREATE applications TABLE ( for user application for requesting of different data )
CREATE TABLE IF NOT EXISTS applications (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   title VARCHAR(100),
   content TEXT,           -- purpose of application

   -- status can be ( approved, rejected, processing )
   -- processing -> is submitted but not seen by admin
   status VARCHAR(10),     -- it tells if application is considered or not
   issuer_email VARCHAR(30),
   dataset_id VARCHAR(30),

   FOREIGN KEY (issuer_email) REFERENCES users(email),
   FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);


------------------------------- TEST DATABASE ----------------------------------
-- \c test;

-- CREATE TABLE IF NOT EXISTS s_assets (
--    id VARCHAR(30) PRIMARY KEY,
--    name TEXT,
--    file_url TEXT
-- );