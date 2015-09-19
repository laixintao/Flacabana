#!flask/bin/python

from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    user_anget = request.headers.get('User-Agent')
    return render_template('index.html')

@app.route('/usr/<name>')
def user(name):
    return render_template('user.html',name=name)

if __name__=='__main__':
    # app.run(debug=True)
    app.run()