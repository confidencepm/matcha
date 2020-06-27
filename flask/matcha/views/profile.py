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

user = Blueprint("profile", __name__)


@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.get_user({"username": session.get("username")})

    errors = []
    location = []
    blocked = user["blocked"]
    users = db.users({"_id": {"$nin": blocked}, "completed": 1})
    # if user["completed"] == 1:
    #     valid_users = [
    #         check_user
    #         for check_user in users
    #         if check_user["completed"] == 1 and get_howfar(user, check_user) < 20
    #     ]
    # else:
    #     valid_users = []

    # update user details
    if request.method == "POST":
        if request.form.get("submit") == "update":
            print(f"Debug {request.form}")
            username = html.escape(request.form.get("username"))
            email = html.escape(request.form.get("email"))
            firstname = html.escape(request.form.get("firstname"))
            lastname = html.escape(request.form.get("lastname"))
            image = request.files.get("image")

            if not re.match("^[A-Za-z][A-Za-z0-9]{2,49}$", username):
                errors.append(
                    "The username must be an alpha numeric value, 3 - 50 characters long."
                )
            elif user["username"] != username and db.get_user({"username": username}):
                errors.append("The username is already taken please choose another")
            else:
                user["username"] = username
                session["username"] = username

            if not re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$", email
            ):
                errors.append("invalid email format")
            elif user["email"] != email and db.get_user({"email": email}):
                errors.append("The email is already taken please choose another one")
            else:
                user["email"] = email
            if not firstname:
                errors.append("Firstname may not be empty")
            elif not re.match("^[A-Z][A-Za-z-]{2,24}$", firstname):
                errors.append(
                    "Firstname must begin with a capital letter and contain only: letters and/or -'s"
                )
            else:
                user["firstname"] = firstname

            if not lastname:
                errors.append("Lastname may not be empty")
            elif not re.match("^[A-Z][ A-Za-z-]{2,24}$", lastname):
                errors.append(
                    "Lastname must begin with a capital letter and contain only: letters, spaces and/or -'s"
                )
            else:
                user["lastname"] = lastname

            if image:
                pic_name = save_picture(image)
                user["image_name"] = pic_name

            if not errors:
                db.update_user(user["_id"], user)
                flash("User details updated", "success")
                return redirect(url_for("profile.profile"))

            for error in errors:
                flash(error, "danger")

        # update user password
        if request.form.get("submitPwd") == "update":
            # print(f"Debug {request.form}")
            password = html.escape(request.form.get("current_password"))
            new_password = html.escape(request.form.get("new_password"))
            check_new_password = html.escape(request.form.get("new_password_repeat"))
            # print("Debug2 ", password, new_password, check_new_password)
            if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
                errors.append("Incorrect password")
            elif new_password:
                # fixme
                # if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{5,25}$", new_password):
                #     print("Password error")
                #     errors.append('The password must have an uppercase, lowercase and a digit')
                if check_new_password != new_password:
                    errors.append("The two passwords do not match")
                else:
                    salt = bcrypt.gensalt()
                    user["password"] = bcrypt.hashpw(new_password.encode("utf-8"), salt)
                    db.update_user(user["_id"], user)

            if not errors:
                print("Updating password")
                db.update_user(user["_id"], user)
                flash("Password updated", "success")
            else:
                for error in errors:
                    flash(error, "danger")

        # update profile
        if request.form.get("submit") == "bioupdate":
            gender = request.form.get("gender")
            sexuality = request.form.get("sexo")
            interests = request.form.getlist("interests")
            bio = html.escape(request.form.get("bio"))
            image = request.files.get("image2")
            if not interests:
                interests = ["none"]
            if not bio:
                errors.append("Bio may not be empty")
            elif len(bio) > 500:
                errors.append("The Bio may not be longer than 500 characters")
            else:
                user["bio"] = bio

            if image:
                pic_name = save_picture(image)
                user["image_name"] = pic_name

            elif user["image_name"] == "default.png":
                errors.append("Please update your photo.")

            if not errors:
                user["gender"] = gender
                user["sex"] = sexuality
                user["interests"] = interests
                user["completed"] = 1
                location = request.form.get("location")
                print(f"Location: {location}")
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
                user["location"] = location
                user["latlon"] = [lat, lon]
                db.update_user(user["_id"], user)
                flash("Profile updated", "success")
                return redirect(url_for("profile.profile"))

            for error in errors:
                flash(error, "danger")

        if request.form.get("submit") == "Upload":
            # print(valid_users)
            image_count = len(user["gallery"])
            if image_count < 4:
                image = request.files.get("image3")
                if image:
                    gallery_img = save_gallery(image)
                    user["gallery"].append(gallery_img)

                    db.update_user(user["_id"], user)
                    return redirect(url_for("profile.profile"))
            else:
                flash("You can only have 4 pictures in your gallery", "danger")

    viewers = []
    for id in user["views"]:
        viewers.append(db.get_user({"_id": ObjectId(id)}))

    likes = []
    for username in user["liked"]:
        likes.append(db.get_user({"username": username}))

    matched = []
    for username in user["matched"]:
        matched.append(db.get_user({"username": username}))


    blocked = []
    for user_id in user['blocked']:
        blocked.append(db.get_user({"_id": user_id}))


    online_users = list(logged_in_users.keys())
    return render_template(
        "user/profile.html",
        logged_in=session.get('username'),
        current_user=user,
        online_users=online_users,
        viewers=viewers,
        likes=likes,
        matched=matched,
        blocked=blocked
    )


@user.route("/profile/view/<user_id>")
@login_required
@finish_profile
def view_profile(user_id):
    id = ObjectId(user_id)
    current_user = db.get_user({"username": session.get("username")})

    user = db.get_user({"_id": id})
    user["fame-rating"] = int((user["fame-rating"] / 10) - 1)
    online_users = list(logged_in_users.keys())
    return render_template(
        "user/view_profile.html",
        logged_in=session.get('username'),
        user=user,
        online_users=online_users,
        current_user=current_user
    )

