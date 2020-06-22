from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from functools import wraps
import os, secrets, re, html, pymongo, bcrypt
# from werkzeug import secure_filename
from PIL import Image
from matcha import db, app, logged_in_users
from matcha.utils import *
from bson.objectid import ObjectId

from datetime import date
from bson import ObjectId

user = Blueprint('profile', __name__)

@user.route('/profile',  methods=['GET', 'POST'])
@login_required
def profile():
    user = db.get_user({'username' : session.get('username')})
    admin = False

    if user['_id'] == ObjectId(b'bobisadmin!!'):
        admin = True
    errors = []
    location = []
    blocked = user['blocked']
    users=db.users({'_id' : { '$nin' : blocked }, 'completed' : 1})
    if user['completed'] == 1:
       valid_users = [check_user for check_user in users if check_user['completed'] == 1 and get_howfar(user, check_user) < 20]
    else:
        valid_users = []

    if request.method == 'POST':
        if request.form.get('submit') == 'update':
            username = html.escape(request.form.get('username'))
            email = html.escape(request.form.get('email'))
            firstname = html.escape(request.form.get('firstname'))
            lastname = html.escape(request.form.get('lastname'))
            image_file = request.files.get('image')
            password = html.escape(request.form.get('current_password'))
            new_password = html.escape(request.form.get('new_password'))
            check_new_password = html.escape(request.form.get('new_password_repeat'))
            
            if not new_password:
                if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    errors.append('Incorrect password')
            elif new_password:
                if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{5,25}$", new_password):
                    errors.append('The password must have an uppercase, lowercase and a digit')
                elif check_new_password != new_password:
                    errors.append('The two passwords do not match')
                else:
                    salt = bcrypt.gensalt()
                    user['password'] = bcrypt.hashpw(new_password.encode('utf-8'), salt)
                           
            if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', username):
                errors.append('The username must be an alpha numeric value, 3 - 50 characters long.')
            elif user['username'] != username and db.get_user({'username': username}):
                errors.append("The username is already taken please choose another")
            else:
                user['username'] = username
                session['username'] = username

            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$', email):
                errors.append('invalid email format')
            elif user['email'] != email and db.get_user({'email' : email}):
                errors.append("The email is already taken please choose another one")
            else:
                user['email'] = email
            if not firstname:
                errors.append('Firstname may not be empty')
            elif not re.match('^[A-Z][A-Za-z-]{2,24}$', firstname):
                errors.append('Firstname must begin with a capital letter and contain only: letters and/or -\'s')
            else:
                user['firstname'] = firstname

            if not lastname:
                errors.append('Lastname may not be empty')
            elif not re.match('^[A-Z][ A-Za-z-]{2,24}$', lastname):
                errors.append('Lastname must begin with a capital letter and contain only: letters, spaces and/or -\'s')
            else:
                user['lastname'] = lastname

            if image_file:
                pic_name = save_picture(image_file)
                user['image_name'] = pic_name

            if not errors:
                db.update_user(user['_id'], user)
                return redirect( url_for('profile.profile') )

            for error in errors:
                flash(error, 'danger')

        if request.form.get('submit') == 'bioupdate':
            gender = request.form.get('gender')
            sex = request.form.get('sexo')
            intret = request.form.getlist('interests')
            bio = html.escape(request.form.get('bio'))
            image_file = request.files.get('image2')
            if not intret:
                intret = ["none"]
            if not bio:
                errors.append('Bio may not be empty')
            elif len(bio) > 500:
                errors.append('The Bio may not be longer than 500 characters')
            else:
                user['bio'] = bio

            if image_file :
                pic_name = save_picture(image_file)
                user['image_name'] = pic_name

            elif user['image_name'] == "default.png":
                errors.append('Please update your photo.')

            if not errors:
                user['gender'] = gender
                user['sex'] = sex
                user['interests'] = intret
                user['completed'] = 1
                location = request.form.get('location')
                # latlon1 = request.form.get('latlon')
                location = location.split(",")
                # location_send = request.form.get('autocomplete')

                # if location_send:
                #     user['location'] = location_send.split(",")
                #     print ('location',user['location'])
                #     user['latlon'] = latlon1.split(",")
                #     print('user latlon',user['latlon'])
                # else:
                lat = location.pop(3)
                lon = location.pop(3)
                user['location'] = location
                user['latlon'] = [lat, lon]
                db.update_user(user['_id'], user)
                flash('Bio updated', 'success')
                return redirect( url_for('profile.profile'))

            for error in errors:
                flash(error, 'danger')

        if request.form.get('submit') == 'Upload':
            # print(valid_users)
            total_amnt = len(user['gallery'])
            if total_amnt < 4:
                image_file = request.files.get('image3')
                if image_file:
                    gallery_img = save_gallery(image_file)
                    user['gallery'].append(gallery_img)

                    db.update_user(user['_id'], user)
                    return redirect( url_for('profile.profile') )
            else:
                flash('You can only have 4 pictures in your gallery', 'danger')

    viewers = []
    for id in user['views']:
        viewers.append(db.get_user({'_id': ObjectId(id)}))

    flirts = []
    for username in user['flirted']:
        flirts.append(db.get_user({'username': username}))

    matched = []
    for username in user['matched']:
        matched.append(db.get_user({'username': username}))

    online_users = list(logged_in_users.keys())
    return render_template('user/profile.html', logged_in=session.get('username'), current_user=user, users=valid_users, admin=admin, viewers=viewers, flirts=flirts, matched=matched, online_users=online_users )



@user.route('/profile/view/<user_id>')
@login_required
@finish_profile
def view_profile(user_id):
    id = ObjectId(user_id)
    current_user = db.get_user({'username': session.get('username')})

    user = db.get_user({'_id': id})
    user['fame-rating'] = int((user['fame-rating'] / 10) - 1)
    online_users = list(logged_in_users.keys())
    return render_template('user/view_profile.html', logged_in=session.get('username'), user=user, current_user=current_user, online_users=online_users)
