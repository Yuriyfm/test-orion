from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# В данном модуле происходит создание приложения Flask и хрянаятся настройки app.config
app = Flask(__name__)
db_uri = "postgresql://postgres:qwerty@localhost:5432/oriondb"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

from orion import views, models
