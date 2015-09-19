#!flask/bin/python

from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask import render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
boostrap = Bootstrap(app)

@app.route('/')
def index():
    # user_anget = request.headers.get('User-Agent')
    return "hello"

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

if __name__=='__main__':
    app.run(debug=True)

