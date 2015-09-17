from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

lm = LoginManager
lm.setup_app(app)
oid = OenpID(app,os.path.join(basedir,'tmp'))

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

