#!flask/bin/python

import os
from functools import wraps
# from threading import Thread
from flask import Flask, render_template,\
    session, redirect,\
    url_for,request,flash,\
    abort
from datetime import datetime
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,PasswordField,BooleanField, \
    IntegerField
from wtforms.validators import Required,Length,Email,EqualTo
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
# from flask.ext.mail import Mail, Message
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin,AnonymousUserMixin
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user,logout_user,current_user


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db',MigrateCommand)
# mail = Mail(app)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW |
                    Permission.COMMENT|
                    Permission.WRITE_ARTICLES,True),
            'Moderator':(
                Permission.FOLLOW|
                Permission.COMMENT|
                Permission.WRITE_ARTICLES|
                Permission.MODERATE_COMMENTS,False
            ),
            'Administrator':(
                0xff,False
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.name = r
                role.permissions = roles[r][0]
                role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    truename = db.Column(db.String(32))
    school_id = db.Column(db.Integer)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow())

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self,permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        "The password can only be read only"
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self,psw):
        self.password_hash = generate_password_hash(psw)

    def verify_password(self,psw):
        return check_password_hash(self.password_hash,password=psw)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#
# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated():
        current_user.ping()
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None:
            user = User(username=form.name.data)
            # db.session.add(user)
            session['known'] = False
            # if app.config['FLASKY_ADMIN']:
            #     send_email(app.config['FLASKY_ADMIN'], 'New User',
            #                'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))

# Login
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/secret')
@login_required
def secret():
    return "only authenticated users are allowed!"

class LoginForm(Form):
    id = StringField('User id',validators=[Required(),Length(1,64)])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in ')
    submit = SubmitField('Log in')

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.id.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(url_for('index'))
        flash('Invalid username or password!')
    return render_template('login.html',form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))

class RegistrationForm(Form):
    username = StringField('Username', validators=[
             Required(), Length(1, 64), ])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    school_id = IntegerField('Your school id',validators=[Required()])
    true_name = StringField('Your real name')
    submit = SubmitField('Register')

@app.route("/register",methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is not None:
            flash("Username has already exist!")
            return redirect(url_for('register'))
        user = User(
                username=form.username.data,
                password=form.password.data,
                truename = form.true_name.data,
                school_id = form.school_id.data
        )
        db.session.add(user)
        flash('You can now login.')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Reset psw
class ChangePassword(Form):
    old_password=PasswordField("Old Password",validators=[Required()])
    password = PasswordField('Password', validators=[Required(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Change')

@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html",user = user)

@app.route("/change_psw",methods=["GET","POST"])
@login_required
def change_psw():
    form = ChangePassword()
    if form.validate_on_submit():
        if current_user.verify_password(
                form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Your password changed !")
            db.session.commit()
            return redirect(url_for("user",username=current_user.username))
        else:
            flash("Invalid password.")
    return render_template('change_psw.html',form=form)

# Permission test
@app.route("/admin")
@login_required
@admin_required
def for_admins_only():
    return "For admin!"

if __name__ == '__main__':
    manager.run()
