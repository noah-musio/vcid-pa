import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Konfiguration für Dev-Umgebung lokal, Quelle: Eigenentwicklung 
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
DATABASE_URI = 'mysql+pymysql://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser="mysql",
    dbpass="mysql",
    dbhost="localhost",
    dbname="vcid"
)
