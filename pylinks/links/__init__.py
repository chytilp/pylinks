from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from config import Config

DEFAULT_GET_LIMIT = 100

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
  Config.DB_USER, Config.DB_PASS, Config.DB_HOST, Config.DB_PORT, Config.DATABASE))
db = SQLAlchemy(app)
api = Api(app)
