#!flask/bin/python

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    user_anget = request.headers.get('User-Agent')
    return '<p>Your Browser is %s</p>' %user_anget

@app.route('/usr/<name>')
def user(name):
    return '<h1>Hello,%s</h1>' % name

if __name__=='__main__':
    app.run(debug=True)