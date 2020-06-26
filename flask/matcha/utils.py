from flask import url_for, redirect, session, flash, request
from functools import wraps
from matcha import db, app
import os, secrets
from werkzeug.utils import secure_filename
from PIL import Image
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import *
from geopy.distance import *

def get_user_location(current_user):
    user_loca = (current_user['latlon'][0], current_user['latlon'][1])
    return user_loca

def get_howfar(current_user, users):
    return (geodesic(get_user_location(current_user), get_user_location(users)).km)

# def allvs1():
#     current_user=db.get_user({'username' : session.get('username')})
#     users=db.users()
#     valid_users = [user for user in users if get_howfar(current_user, users) < 20]

# This is used to force the user to login before being allowed to 
# get access to a route
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('username') is None:
            flash("Please login in first", 'info')
            return redirect( url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

# needed to force the user to finish creating their bio before anything.
def finish_profile(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = db.get_user({'username': session.get('username')})
        if user is None:
            return redirect( url_for('auth.login', next=request.url))
        if user['completed'] == 0:
            flash("Please finish your profile first", 'info')
            return redirect( url_for('profile.profile', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def save_picture(form_pic):
    rand_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_pic.filename))
    pic_fn =  rand_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_fn)

    # form_pic.save(pic_path)
    i = Image.open(form_pic.stream)
    i.thumbnail((200,200))

    i.save(pic_path)
    return pic_fn

def save_gallery(form_pic):
    rand_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_pic.filename))
    pic_fn =  rand_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/gallery_pics', pic_fn)

    # form_pic.save(pic_path)
    i = Image.open(form_pic.stream)
    i.thumbnail((200,200))

    i.save(pic_path)
    return pic_fn

def send_mail(reciever, subject='email confirmation', text=None, html=None):
    user = db.get_user({'username' : reciever}, {'username' :1 , 'email': 1})

    # Check if the reciever is a username.

    # Set up the user information.
    port = 465
    password = 'C108629d'

    sender_email = "cmukwind@student.wethinkcode.co.za"
    receiver_email = user['email']
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    if not text:
        text = """\
        Hi,{}
        Welcome to Matcha.
        Copy the URL below to confirm your email:
        http://localhost:5000/confirm?jrr={}""".format(user['username'],user['_id'])
        
    if not html:
        html = """\
        <html>
        <body>
            <p>Hi,{}<br>
            Welcome to Matcha.<br>
            Click the link below to confirm your email:
            <a href="http://localhost:5000/confirm?jrr={}">Confirm Email</a>
            </p>
        </body>
        </html>
        """.format(user['username'],user['_id'])
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    email_context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=email_context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


# Creata a fucntion that finds the similarity ration betwwen two users interests.
def similarity_perc(list1, list2):
    # Calculation the percentage similarity of the two lists.
    # print('list 1:', list1)
    # print('list 2:', list2)
    if not list1 or not list2:
        return 0
    res = len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100
    return res


# Calculate the users fame rating
def calculate_fame(user):
    account_count = db.count_users()
    user_liked = len(user['liked'])
    fame_rate = user_liked / account_count * 100

    # Update the user information.
    user['fame-rating'] = fame_rate
    db.update_user(user['_id'], user)
    return fame_rate



# filter out the user with the specific interest.
def filter_interest(users, interest):
    valid_users = [user for user in users if set(interest).issubset(set(user['interests']))]
    return valid_users

# Filter out the users with a specific location.
def filter_location(users, location):
    valid_users = [user for user in users if location in user['location'][2]]
    return valid_users

# Filter out users based on the given age
def filter_age(users, age):
    # print('in filter age', age)
    valid_users = [user for user in users if age <= int(user['fame-rating'])]
    return valid_users
