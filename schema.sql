-- CONNECT TO POSTGRES
-- sudo -u postgres psql

-- RUN THE BELOW COMMAND TO EXECUTE THIS SQL SCRIPT
-- psql --host=localhost --port=5432 -U root --dbname=gehackathon
   --echo-errors --file="../Projects/GEHackathon/schema.sql" --no-password 

-- CONNECT TO DATABASE
\c gehackathon;

-- CREATE TABLE `users`
CREATE TABLE IF NOT EXISTS users (
   email VARCHAR(30) PRIMARY KEY NOT NULL,
   username VARCHAR(20) NOT NULL UNIQUE,
   passwd VARCHAR(100)
);

-- CREATE TABLE `admin`
CREATE TABLE IF NOT EXISTS admin (
   username VARCHAR(20) PRIMARY KEY NOT NULL,
   passwd VARCHAR(100)
);

-- CREATE TABLE `datasets` ( datasets will have reference to `s_assets` and `d_assets`)
CREATE TABLE IF NOT EXISTS datasets (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   name TEXT,
   description TEXT,
   assets VARCHAR[] -- id's of the `s_assets` TABLE
);

-- CREATE s_assets TABLE [ source files -> (text files, audio files, images) ]
-- all metadata for an asset are stores in `source_assets`
-- and the id is referenced from `d_assets`
CREATE TABLE IF NOT EXISTS s_assets (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   fname TEXT,
   asset_data BYTEA,
   mimetype VARCHAR(20),
   tags VARCHAR[]
);

-- CREATE d_assets TABLE ( source files -> text files, audio files, images)
-- no metadata must be referenced using `source_assets`
CREATE TABLE IF NOT EXISTS d_assets (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   asset_data BYTEA,
   FOREIGN KEY (id) REFERENCES s_assets(id)
);

-- CREATE applications TABLE ( for user application for requesting of different data )
CREATE TABLE IF NOT EXISTS applications (
   id VARCHAR(30) PRIMARY KEY NOT NULL,
   title VARCHAR(100),
   content TEXT,       -- purpose of application
   tags VARCHAR[],     -- user can specify which type of data he wants
   time TIMESTAMP,     -- time of submission

   -- status can be ( approved, rejected, processing )
   -- processing -> is submitted but not seen by admin
   status VARCHAR(10)    -- it tells if application is considered or not
   
   issuer_email VARCHAR(30),
   dataset_id VARCHAR(30),

   FOREIGN KEY (issuer_id) REFERENCES users(email),
   FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);