#!flask/bin/python

from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    user_anget = request.headers.get('User-Agent')
    return '<p>Your Browser is %s</p>' %user_anget

@app.route('/usr/<name>')
def user(name):
    return '<h1>Hello,%s</h1>' % name

@app.route('/cookie')
def cookie():
    response = make_response('<h1>this document carries a cookie!</h1>')
    response.set_cookie('answer','42')
    return response

@app.route('/redirect')
def redirect_page():
    return redirect('http://www.kawabangga.com')

if __name__=='__main__':
    # app.run(debug=True)
    manager.run()