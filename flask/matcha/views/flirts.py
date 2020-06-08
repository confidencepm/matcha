from matcha import db
from functools import wraps
from flask import render_template, redirect, request, abort, url_for, flash, session, Blueprint
from matcha.utils import *

flirts = Blueprint('flirts', __name__)


@flirts.route('/user/flirt/<string:username>', methods=['GET', 'POST'])
@login_required
@finish_profile
def flirt(username):
    flirter = db.get_user({'username':session.get('username')}, {'flirts': 1, 'username' : 1})
    flirtee = db.get_user({'username':username}, {'flirted': True, 'username' : 1})

    # Flirted is used for people who have liked you.
    flirtee['flirted'].append(session.get('username'))
    # Flirts is for users who you have like
    flirter['flirts'].append(flirtee['username'])
    
    db.update_flirts(flirter['_id'], {'flirts': flirter['flirts']})
    db.update_flirts(flirtee['_id'], {'flirted': flirtee['flirted']})

    return redirect( url_for('main.users') )