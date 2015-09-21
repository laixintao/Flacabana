#!flask/bin/python

from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask import render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask import session,url_for
from flask import flash
from flask.ext.script import Manager

app = Flask(__name__)
boostrap = Bootstrap(app)
moment = Moment(app)
# manager = Manager(app)

app.config['SECRET_KEY'] = 'readlly hard to guess string.'

# SQL config
from flask.ext.sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>'%self.username

@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        # flash("Name commit!")
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['know'] = False
        else:
            session['know'] = True
        session['name']=form.name.data
        return redirect(url_for('index'))
    user_anget = request.headers.get('User-Agent')
    return render_template('index.html',agent=user_anget,
                           current_time=datetime.utcnow(),
                           name=session.get('name'),form=form,
                           know = session.get('know',False))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

# define the form
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required

class NameForm(Form):
    name=StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')

# config flask-migrate
from flask.ext.migrate import Migrate,MigrateCommand
migrate = Migrate(app,db)
# manager.add_command('db',MigrateCommand)

if __name__=='__main__':
    app.run()


