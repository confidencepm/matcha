from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha import db, logged_in_users
from bson import ObjectId
from functools import wraps
import secrets, re, bcrypt, html
from matcha.utils import *
from datetime import datetime

# import smtplib, ssl
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart


#  Create the blueprint
auth = Blueprint('auth', __name__)


# def calculateAge(birthdate):
#     today = date.today()
#     age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day)) 

#     return age

# Handle the user registration
@auth.route('/register', methods=['GET', 'POST'])
def register():
    blocked = db.get_user(db.get_user({'_id': ObjectId(b'bobisadmin!!')}, {'blocked': 1}))["blocked"]
    errors = []
    details = {
        'username': '',
        'firstname': '',
        'lastname': '',
        'email': '',
        'password': '',
        'gender': '',
        'sexual_orientation': 'bisexual',
        'bio': '',
        'interests': [],
        'likes': [],
        'liked': [],
        'matched': [],
        'blocked': blocked,  # users blocked
        'views': [],
        'rooms': {},
        'notifications': [],
        'fame-rating': 0,
        'location': [],
        'latlon': '',
        'age': 18,
        'image_name': 'default.png',
        'gallery': [],
        'token': secrets.token_hex(16),
        'completed': 0,
        'email_confirmed': 0,
        'last-seen': datetime.utcnow()

    }

    if request.method == 'POST':
        details['username'] = html.escape(request.form.get('username'))
        details['firstname'] = html.escape(request.form.get("firstname"))
        details['lastname'] = html.escape(request.form.get('lastname'))
        details['email'] = html.escape(request.form.get('email'))
        details['password'] = html.escape(request.form.get('password'))
        passwd_confirm = html.escape(request.form.get('password_confirm'))

        # Check the users username
        if not details['username']:
            errors.append('The username cannot be empty')
        if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', details['username']):
            errors.append(
                'The username must be an alpha numeric value beginning with a letter, 3 - 50 characters long.')
        if db.get_user({'username': details['username']}):
            errors.append('The username is already taken')
        # Check the users email
        if db.get_user({'email': details['email']}):
            errors.append('The email is already taken!')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$', details['email']):
            errors.append('invalid email format')
        # check the users password
        # if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{5,25}$", details['password']):
        #     errors.append('The password must have an uppercase, lowercase and a digit, 5 - 25 characters long.')
        if passwd_confirm != details['password']:
            errors.append('The two passwords do not match')
        # Check the users firstname
        if not re.match('^[A-Z][a-zA-Z-]{1,24}$', details['firstname']):
            errors.append('A name must start with a capital letter, and a have no more than 25 characters')
        try:
            # details['age'] = calculateAge(request.form.get('dob')) //
            details['age'] = int(request.form.get('age'))
            if details['age'] < 18 or details['age'] > 100:
                errors.append("You need to be between 18 and 100 to use this site")
        except ValueError:
            errors.append("Age needs to be a number")
        # Check the user lastname
        if not re.match('^[A-Z][ a-zA-Z-]{1,24}$', details['lastname']):
            errors.append('The lastname must start with a capital letter, and have 2-24 charaters')

        if not errors:
            salt = bcrypt.gensalt()
            details['password'] = bcrypt.hashpw(details['password'].encode('utf-8'), salt)
            db.register_user(details)
            send_mail(details['username'])
            flash("Please check your email for confirmation", 'success')
            return redirect(url_for('auth.login'))

        for error in errors:
            flash(error, 'danger')

    return render_template('auth/register.html', details=details)


@auth.route('/confirm', methods=['GET', 'POST'])
def confirm():
    errors = []
    if request.method == 'GET':
        user_id = ObjectId(request.args.get('jrr'))

        user = db.get_user({'_id': user_id})

        if user:
            db.update_likes(user_id, {'email_confirmed': 1})
            flash('Email confirmed', 'success')
            return redirect(url_for('auth.login'))
        else:
            errors.append("Incorrect username or password")
            for error in errors:
                flash(error, 'danger')

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    errors = []
    details = {
        'username': '',
        'password': ''
    }

    if request.method == 'POST':
        details['username'] = html.escape(request.form.get('username'))
        details['password'] = html.escape(request.form.get('password'))
        user = db.get_user({'username': details['username']})

        if not user:
            errors.append("Incorrect username or password")
        elif not user['email_confirmed']:
            errors.append('Please check your email for confirmation')
        elif not bcrypt.checkpw(details['password'].encode('utf-8'), user['password']):
            errors.append('Incorrect username or password')

        if not errors:
            session['username'] = details['username']
            flash('Successful login', 'success')
            if not details['username'] in logged_in_users:
                logged_in_users[details['username']] = ''
            calculate_fame(user)
            return redirect(url_for('main.home'))
        for error in errors:
            flash(error, 'danger')

    return render_template('auth/login.html', details=details)


# Route for the logout
@auth.route('/logout')
def logout():
    user = db.get_user({'username': session.get('username')}, {'last-seen': 1})

    user['last-seen'] = datetime.utcnow()
    db.update_likes(user['_id'], {'last-seen': user['last-seen']})

    logged_in_users.pop(session.pop("username"), None)

    # session.pop('username')
    return redirect(url_for('main.home'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    errors = []
    details = {
        'username': ''
    }
    if request.method == 'POST':
        username = request.form.get('username')
        user = db.get_user({'username': username})

        if not username:
            errors.append('The username cannot be empty')
        if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', username):
            errors.append('Invalid username')
        if not user:
            errors.append('No such user found, please register an account, peasant')

        if not errors:
            subject = 'Forgot Password'
            text = """\
                    Hi,{}
                    Welcome to Matcha.
                    Copy the URL below to reset your password:
                    http://localhost:5000/reset_password?jrr={}""".format(user['username'], user['_id'])
            html = """\
                    <html>
                    <body>
                        <p>Hi,{}<br>
                        Welcome to Matcha.<br>
                        Click the link below to reset your password:
                        <a href="http://127.0.0.1:5000/reset_password?jrr={}">Reset Password</a>
                        </p>
                    </body>
                    </html>
                    """.format(user['username'], user['_id'])
            send_mail(username, subject, text, html)
            flash('Please check your email to reset your password', 'success')
        for error in errors:
            flash(error, 'danger')

    return render_template('auth/forgot_password.html', details=details)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    errors = []

    if request.method == 'GET':
        user_id = ObjectId(request.args.get('jrr'))
        # user = db.get_user({'_id': id})

    if request.method == 'POST':
        user_id = ObjectId(request.args.get('jrr'))
        user = db.get_user({'_id': user_id})
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        if not re.match('[A-Za-z0-9]', password):
            errors.append('The password must have an uppercase, lowercase and a digit')
        if password_repeat != password:
            errors.append('The two passwords do not match')

        if not errors:
            salt = bcrypt.gensalt()
            user['password'] = bcrypt.hashpw(password.encode('utf-8'), salt)
            db.update_user(user['_id'], user)
            return redirect(url_for('auth.login'))

        for error in errors:
            flash(error, 'danger')

    return render_template('auth/reset_password.html')
