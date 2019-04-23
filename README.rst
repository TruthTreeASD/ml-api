ml-api
====== 
A rest api service for machine learning in TruthTree Project.

Local deployment:
-----------------
NOTE: Deploying this application locally requires a good amount of free memory (~3GB). 

1.	Install docker (Refer to https://docs.docker.com/) 

2.	Clone ml-api repo.
‘git clone https://github.com/TruthTreeASD/ml-api.git‘

3.	Build the docker image for ml-api.
‘cd ml-api ; docker build -t <image-name> .’

4.	Run PostgreSQL as a docker container (Refer https://hub.docker.com/_/postgres).

docker pull postgres
docker run --net=host -d postgres

6.	Export the required environment variables.
# This will use the postgres created in step 5
export DATABASE_URL='postgres://postgres:postgres@localhost/postgres' 
export APP_SETTINGS=config.DevelopmentConfig

7.	Modify deploy-rest-ml.sh and add 'python3.6 app/db.py -p app/data/'. This will create tables in the database and populate the data.
#Serve the web app through gunicorn
function launch_app() {
    python3.6 app/db.py -p app/data/
    gunicorn app:app --timeout 300 --bind 0.0.0.0:8000
}
NOTE: The script db.py will create a table for each file(.csv) present inside the path specified. If you want to populate the database with new data or you want new tables to be created in the databse,copy the datafile as <tablename>.csv to app/data and run the script again.

8.	Now that we have the database ready, we can run ML REST Server as a docker container (image-id from step 4).

docker run -e DATABASE_URL -e APP_SETTINGS -v $PWD:/app  --net=host -it <image-id>

This will take a good 5 minutes to complete the data generation and precomputation.
Open http://localhost:8000/api on your browser and you should be able to see the swagger documentation of the APIs.

