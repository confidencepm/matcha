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


#Deprecated
def get_user_location(current_user):
    """ Get the latitude and longitude of a user

    ARGS:
    current_user : dictionary. a list containing information that pertains the user

    returns:
    Location of a user(you can also explain)
    """
    user_location = (current_user['latlon'][0], current_user['latlon'][1])
    return user_location

#Deprecated
def get_howfar(current_user, users):
    """ Get the distance between two
    """
    return (geodesic(get_user_location(current_user), get_user_location(users)).km)

# get access to a route
def login_required(f):
    @wraps(f)
    #extend the functionalioty of the function f, use as @login_required decorator.
    def wrapper(*args, **kwargs):
        if session.get('username') is None:
            flash("Please login in first", 'info')
            return redirect( url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

# needed to force the user to finish creating their bio before anything.
def finish_profile(f):
    @wraps(f)#extend the functionalioty of the function f, use as @login_required decorator.
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

    i = Image.open(form_pic.stream)
    i.thumbnail((200,200))

    i.save(pic_path)
    return pic_fn

def send_mail(reciever, subject='email confirmation', text=None, html=None):
    """ send and Auth email for account registration

    ARGS:
    reciever: string. username of the new account the email is sent to
    subject : string. subject of the verification email "email confirmation by default"
    text    : string. the email body  

    returns: nothing.
        uses the smtplib.SMTP_SSL() as a server to send a verification email
        to a newly registered user.
    """
    user = db.get_user({'username' : reciever}, {'username' :1 , 'email': 1})

    port = 465
    password = 'C108629d'

    sender_email = "emanana@student.wethinkcode.co.za"
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
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    email_context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=email_context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def similarity_perc(list1, list2):
    """ computation of the similar interest between user
        check if list1 is not in list two. else return a number counting
        similar interest

    ARGS:
    list1: list. a list containing the interest of user 1
    list2: list containing interest of user 2

    return : int.
        if the users have similar interest, return a count, that tallys the interest
    """
    if not list1 or not list2:
        return 0
    res = len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100
    return res


def calculate_fame(user):
    """ compute the the users populariy.
        if no one liked th user fame or popolarity is 0
        otherwise compute the (mean of likes )* 100

        Args:
        user : dict. dictionary/object of users info.

        returns:
            updates the fame/populariry rating in the databse
    """
    account_count = db.count_users()
    user_liked = len(user['likes'])
    if user_liked == 0:
        fame_rate = 0
    else:
        fame_rate = (user_liked / account_count) * 100

    user['fame-rating'] = int(fame_rate)
    db.update_user(user['_id'], user)



# filter out the user with the specific interest.
def filter_interest(users, interest):
    """ filter users in A"users" common interest A"interest

    Args: 
    users: list. An iterable containing data that pertains the user
    interest: iterable(list) . an iterable of desired interest.

    return:
        a list of users with desired interest
    """
    valid_users = [user for user in users if set(interest).issubset(set(user['interests']))]
    return valid_users

# Filter out the users with a specific location.
def filter_location(users, location):
    valid_users = [user for user in users if location in user['location'][2]]
    return valid_users

# Filter out users based on the given age
def filter_age(users, age):
    if age == 29:
        valid_users = [user for user in users if user['age'] >= 18 and user['age'] <= age]
    elif age == 39:
        valid_users = [user for user in users if user['age'] >= 30 and user['age'] <= age]
    elif age == 100:
        valid_users = [user for user in users if user['age'] >= 40 and user['age'] <= age]
    return valid_users

def filter_fame(users, fame):
    """Filter out users based on the given fame

        Args:
        users: list. An iterable containing data that pertains the user
        fame : int . a number denoting the popularity of a user.
        returns:
        a list users based on the given fame
    """
    print("Fame: ", fame)
    if fame == 10:
        valid_users = [user for user in users if user['fame-rating'] >= 0 and user['fame-rating'] < fame]
    elif fame == 20:
        valid_users = [user for user in users if user['fame-rating'] >= 10 and user['fame-rating'] < fame]
    elif fame == 30:
        valid_users = [user for user in users if user['fame-rating'] >= 20 and user['fame-rating'] < fame]
    elif fame == 40:
        valid_users = [user for user in users if user['fame-rating'] >= 30 and user['fame-rating'] < fame]
    elif fame == 50:
        valid_users = [user for user in users if user['fame-rating'] >= 40 and user['fame-rating'] < fame]
    elif fame == 60:
        valid_users = [user for user in users if user['fame-rating'] >= 50 and user['fame-rating'] < fame]
    elif fame == 70:
        valid_users = [user for user in users if user['fame-rating'] >= 60 and user['fame-rating'] < fame]
    elif fame == 80:
        valid_users = [user for user in users if user['fame-rating'] >= 70 and user['fame-rating'] < fame]
    elif fame == 90:
        valid_users = [user for user in users if user['fame-rating'] >= 80 and user['fame-rating'] < fame]
    elif fame == 100:
        valid_users = [user for user in users if user['fame-rating'] >= 90 and user['fame-rating'] < fame]
    return valid_users
