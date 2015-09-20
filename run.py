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

app = Flask(__name__)
boostrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'readlly hard to guess string.'

@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name!=form.name.data:
            flash('Oh you changed your name!')
        session['name']=form.name.data
        return redirect(url_for('index'))
    user_anget = request.headers.get('User-Agent')
    return render_template('index.html',agent=user_anget,
                           current_time=datetime.utcnow(),name=session.get('name'),form=form)

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

if __name__=='__main__':
    app.run(debug=True)

