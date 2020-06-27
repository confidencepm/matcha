from matcha import db, logged_in_users, valid_users
from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from bson.objectid import ObjectId
from functools import wraps, cmp_to_key
from matcha.utils import *
import html

main = Blueprint("main", __name__)


# Create the route for the home page
@main.route("/")
@login_required
@finish_profile
def home():
    user = db.get_user({"username": session.get("username")}, {"notifications": 1})
    return render_template(
        "home.html", logged_in=session.get("username"), current_user=user
    )


@main.route("/users")
@login_required
@finish_profile
def users():
    # valid_users = []
    # users = db.users({'_id' : { '$nin' : blocked }, {'completed' : 1})
    current_user = db.get_user({"username": session.get("username")})
    blocked = current_user["blocked"]
    opp_gen = "Male" if current_user["gender"] == "Female" else "Female"
    gen = current_user["gender"]

    if current_user["sexual_orientation"] == "heterosexual":
        users = list(
            db.users(
                {
                    "_id": {"$nin": blocked},
                    "gender": opp_gen,
                    "sexual_orientation": {"$nin": ["homosexual"]},
                }
            )
        )
    elif current_user["sexual_orientation"] == "homosexual":
        users = list(
            db.users(
                {
                    "_id": {"$nin": blocked},
                    "gender": gen,
                    "sexual_orientation": {"$nin": ["heterosexual"]},
                }
            )
        )
    else:
        users = list(
            db.users(
                {
                    "$and": [
                        {"_id": {"$nin": blocked}},
                        {
                            "$or": [
                                {"sexual_orientation": "bisexual"},
                                {
                                    "$or": [
                                        {
                                            "$and": [
                                                {"sexual_orientation": "homosexual"},
                                                {"gender": gen},
                                            ]
                                        },
                                        {
                                            "$and": [
                                                {"sexual_orientation": "heterosexual"},
                                                {"gender": opp_gen},
                                            ]
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                }
            )
        )

    global valid_users
    current_user = db.get_user({"username": session.get("username")})
    # for user in users:
    #     if user['username'] != current_user['username']:
    #         if similarity_perc(current_user['interests'], user['interests']) > 49.0:
    #             valid_users.append(user)
    valid_users = [
        user
        for user in users
        if user["username"] != current_user["username"]
        and similarity_perc(current_user["interests"], user["interests"]) >= 0
        and user["completed"] == 1
        and get_howfar(current_user, user) < 20
    ]

    return render_template(
        "user/users.html",
        logged_in=session.get("username"),
        users=valid_users,
        current_user=current_user,
        search=True,
    )

@main.route("/users/username/search", methods=["GET", "POST"])
@login_required
@finish_profile
def search_username():
    global valid_users
    if request.method == "POST":
        username = request.form.get("username")
        print(username)
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        valid_users = list(
            db.users({"_id": {"$nin": blocked}, "completed": 1, "username": username})
        )

        # Add the filters stuff.
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/interest/search", methods=["GET", "POST"])
@login_required
@finish_profile
def search_interest():
    global valid_users

    if request.method == "POST":
        interest = request.form.get("interest")
        interest = (interest.replace(" ", "")).split(",")
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "completed": 1})
        valid_users = filter_interest(users, interest)

        # Add the filters stuff.
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/location/search", methods=["GET", "POST"])
@login_required
@finish_profile
def search_location():
    global valid_users

    if request.method == "POST":
        location = request.form.get("location")
        location = location.split(",")
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "completed": 1})
        valid_users = filter_location(users, location[0])

        # Add the filters stuff.
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/age/search", methods=["GET", "POST"])
@login_required
@finish_profile
def search_age():
    global valid_users
    if request.method == "POST":
        age = request.form.get("age")

        if not age.isnumeric():
            flash("invalid input for age search", "danger")
            return redirect(url_for("main.users"))
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "completed": 1})
        age = int((age.replace(" ", "")).split(",")[0])
        valid_users = filter_age(users, age)

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/fame/<value>", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_fame(value):
    global valid_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Sort":
        sorted_users = valid_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["fame-rating"] > sorted_users[k]["fame-rating"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )
    elif value == "Filter":
        valid_users = [
            user
            for user in valid_users
            if current_user["fame-rating"] >= user["fame-rating"]
        ]
        [print(user["username"], user["fame-rating"]) for user in valid_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/likes", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_likes():
    global valid_users

    sorted_users = valid_users[:]
    current_user = db.get_user({"username": session.get("username")})
    for i in range(len(sorted_users)):
        for k in range(len(sorted_users)):
            if len(sorted_users[i]["flirted"]) > len(sorted_users[k]["flirted"]):
                sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
    [print(user["username"], len(user["flirted"])) for user in sorted_users]

    return render_template(
        "user/users.html",
        logged_in=session.get("username"),
        users=sorted_users,
        current_user=current_user,
        search=True,
    )


@main.route("/users/sort/liked", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_liked():
    global valid_users

    sorted_users = valid_users[:]
    current_user = db.get_user({"username": session.get("username")})
    for i in range(len(sorted_users)):
        for k in range(len(sorted_users)):
            if len(sorted_users[i]["flirts"]) > len(sorted_users[k]["flirts"]):
                sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
    [print(user["username"], len(user["flirts"])) for user in sorted_users]

    return render_template(
        "user/users.html",
        logged_in=session.get("username"),
        users=sorted_users,
        current_user=current_user,
        search=True,
    )


@main.route("/users/sort/age/<value>", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_age(value):
    global valid_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Sort":
        sorted_users = valid_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["fame-rating"] < sorted_users[k]["fame-rating"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )
    elif value == "Filter":
        print("current users fame", current_user["fame-rating"])
        valid_users = filter_age(valid_users, current_user["fame-rating"])
        [print(user["username"], user["fame-rating"]) for user in valid_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/location/<value>", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_location(value):
    global valid_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Distance":
        print("\n location: Distance\n")
        sorted_users = valid_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["fame-rating"] > sorted_users[k]["fame-rating"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )

    elif value == "District":
        valid_users = filter_location(valid_users, current_user["location"][2])
        [print(user["username"], user["fame-rating"]) for user in valid_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/interest/<value>", methods=["GET", "POST"])
@login_required
@finish_profile
def sort_interests(value):
    global valid_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Sort":
        sorted_users = valid_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if (
                    similarity_perc(
                        current_user["interests"], sorted_users[i]["interests"]
                    )
                ) <= (
                    similarity_perc(
                        current_user["interests"], sorted_users[k]["interests"]
                    )
                ):
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )
    elif value == "Filter":
        valid_users = [
            user
            for user in valid_users
            if user["username"] != current_user["username"]
            and similarity_perc(current_user["interests"], user["interests"]) >= 0
        ]

        [print(user["username"], user["fame-rating"]) for user in valid_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=valid_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/user/<b_id>/block", methods=["GET", "POST"])
@login_required
@finish_profile
def block_user(b_id):

    current_user = db.get_user({"username": session.get("username")})
    ob_id = ObjectId(b_id)
    current_user["blocked"].append(ob_id)
    db.update_user(current_user["_id"], current_user)

    return redirect(url_for("main.users"))


@main.route("/user/<b_id>/report", methods=["GET", "POST"])
@login_required
@finish_profile
def report_user(b_id):

    current_user = db.get_user({"username": session.get("username")})
    print("email should send")
    subject = "fake account"
    text = """\
    {}  {} reporting {}
    As a fake account
    """.format(
        current_user["username"], current_user["_id"], b_id
    )

    html = """\
    <html>
    <body>
        <p>{}<br>{} reporting {}<br>
            As a fake account
        </p>
    </body>
    </html>
    """.format(
        current_user["username"], current_user["_id"], b_id
    )
    send_mail("Bobbers", subject, text, html)

    ob_id = ObjectId(b_id)
    current_user["blocked"].append(ob_id)
    db.update_user(current_user["_id"], current_user)

    return redirect(url_for("main.users"))


@main.route("/user/<b_id>/block_for_all", methods=["GET", "POST"])
@login_required
@finish_profile
def block_for_all(b_id):
    # bob_id = ObjectId(b'bobisadmin!!')
    # print(bob_id)
    # users = db.users({'_id' : { '$ne' : bob_id}})
    users = db.users()
    ob_id = ObjectId(b_id)
    for user in users:
        # print (user['username'])
        if not ob_id in user["blocked"]:
            user["blocked"].append(ob_id)
            # print (user['blocked'])
            db.update_user(user["_id"], user)

    return redirect(url_for("main.blocked"))


# @main.route('/users')
# @login_required
# @finish_profile
# def users():
#     # valid_users = []
#     # users = db.users({'_id' : { '$nin' : blocked }, {'completed' : 1})
#     current_user = db.get_user({'username' : session.get('username')})
#     blocked = current_user["blocked"]
#     opp_gen = "Male" if current_user["gender"] == "Female" else "Female"
#     gen = current_user["gender"]

#     if current_user["sexual_orientation"] == "heterosexual":
#         users = list(db.users( {'_id' : { '$nin' : blocked }, 'gender' : opp_gen, 'sexual_orientation' : { '$nin' : ["homosexual"]} } ))
#     elif current_user["sexual_orientation"] == "homosexual":
#         users = list(db.users( {'_id' : { '$nin' : blocked }, 'gender' : gen, 'sexual_orientation' : { '$nin' : ["heterosexual"]} } ))
#     else:
#         users = list(db.users({ '$and' : [ {'_id' : { '$nin' : blocked }}, {'$or': [ { 'sexual_orientation' : "bisexual" }, {'$or': [ { '$and': [ { 'sexual_orientation' : 'homosexual' } , { 'gender' : gen } ] } , { '$and': [ { 'sexual_orientation' : 'heterosexual' }, { 'gender' : opp_gen } ] } ] }]}]}) )

#     global valid_users
#     current_user = db.get_user({'username' : session.get('username')})

#     valid_users = [user for user in users if user['username'] != current_user['username'] and similarity_perc(current_user['interests'], user['interests']) >= 0 and user['completed'] == 1]

#     return render_template('user/users.html', logged_in=session.get('username'), users=valid_users, current_user=current_user, search=True)


@main.route("/blocked", methods=["GET", "POST"])
@login_required
@finish_profile
def blocked():
    users = list(db.users({"completed": 1}))

    return render_template(
        "blocked.html", logged_in=session.get("username"), users=users
    )

