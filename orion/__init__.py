import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import configparser

# В данном модуле происходит создание приложения Flask и подключение к БД SQLAlchemy и flask_migrate


config = configparser.ConfigParser()
# подгружаем данные подключения к базе из config.ini
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
config.read(os.path.join(path, 'config.ini'))
config.read("orion/config.ini")
db_user = config['DEFAULT']['db_user']
db_password = config['DEFAULT']['db_password']
db_name = config['DEFAULT']['db_name']
host = config['DEFAULT']['host']
port = config['DEFAULT']['port']

app = Flask(__name__)
db_uri = f"postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,  db)


from orion.api import handlers
