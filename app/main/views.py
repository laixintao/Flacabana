__author__ = 'laixintao'

from datetime import datetime
from flask import render_template,session,redirect,url_for

from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/',method=['GET','POST'])
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
        return redirect(url_for('.index'))
    # user_anget = request.headers.get('User-Agent')
    return render_template('index.html',
                           # agent=user_anget,
                           current_time=datetime.utcnow(),
                           name=session.get('name'),form=form,
                           know = session.get('know',False))