from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha import db, logged_in_users
from bson import ObjectId
from functools import wraps
import secrets, re, bcrypt, html
from matcha.utils import calculate_fame
from faker import Faker
import random
from datetime import datetime


def seed_users():
    print("Creating fake users please wait...")
    n = 250  # number of users you want to create
    fake = Faker()
    usernames = []
    gender = ['Male', 'Female']
    sexo = ['bisexual', 'heterosexual', 'homosexual']
    city = ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Polokwane']
    gallery = ['dummy1.jpg', 'dummy2.jpg', 'dummy3.jpg', 'dummy4.jpg', 'dummy5.jpg', 'dummy6.jpg', 'dummy7.jpg', 'dummy8.jpg', 'dummy9.jpg']
    interests = ['Traveling', 'Animals', 'Technology', 'Sky-diving', 'Movies', 'Music', 'Cooking', 'Sports', 'Gaming']
    profile_pics = ['dummy1.png', 'dummy2.png', 'dummy3.png', 'dummy4.png', 'dummy5.png', 'dummy6.png', 'dummy7.png',
                    'dummy8.png', 'dummy9.png', 'dummy10.png']

    for x in range(n):
        username = fake.user_name()
        usernames.append(username)

    print("Debug ", len(usernames))
    for i in range(n):
        salt = bcrypt.gensalt()
        details = {'username': usernames[i], 'firstname': fake.first_name(), 'lastname': fake.last_name(),
                   'email': fake.email(), 'password': bcrypt.hashpw('Password1'.encode('utf-8'), salt),
                   'gender': random.choice(gender), 'sexual_orientation': random.choice(sexo), 'bio': fake.text(), 'interests': [],
                   'liked': [], 'matched': [], 'blocked': [], 'views': [], 'rooms': {},
                   'fame-rating': 0, 'location': [], 'latlon': '', 'age': 18, 'image_name': 'dummy1.png', 'gallery': [],
                   'token': secrets.token_hex(16), 'completed': 1, 'email_confirmed': 1, 'last-seen': datetime.utcnow(),
                   'notifications': []}

        max_interests = fake.random_int(3, 9)
        max_likes = fake.random_int(3, 40)
        print("Max ", max_likes)
        details['interests'] = random.sample(interests, max_interests)
        details['likes'] = random.sample(usernames, max_likes)
        details['fame-rating'] = fake.random_int(0, 80)
        details['location'].append(''.join([str(fake.random_int(1, 500)), ' ', fake.word(), ' street']))
        details['location'].append(''.join([fake.word(), 'cliff']))
        details['location'].append(random.choice(city))
        details['location'].append('South Africa')
        details['latlon'] = fake.local_latlng(country_code="ZA", coords_only=True)
        details['age'] = fake.random_int(18, 80)
        details['image_name'] = random.choice(profile_pics)

        index = 0
        while index < 4:
            details['gallery'].append(random.choice(gallery))
            index += 1

        db.register_user(details)
        # calculate_fame(details)
        print(f"user {i} of {n}")
    message = str(n) + ' users created'
    print(message)

    r = db.users()
    for user in r:
        calculate_fame(user)

    if not db.get_user({'username': "admin"}, {'username': 1}):
        salt = bcrypt.gensalt()
        Admin = {
            '_id': ObjectId(b'bobisadmin!!'),
            'username': 'admin',
            'firstname': 'Admin',
            'lastname': 'Admin',
            'email': 'admin@matcha.com',
            'password': bcrypt.hashpw('Password1'.encode('utf-8'), salt),
            'gender': 'Male',
            'sexual_orientation': 'homosexual',
            'bio': 'Hi I am Root',
            'interests': [],
            'likes': [],
            'liked': [],
            'matched': [],
            'blocked': [],
            'views': [],
            'rooms': {},
            'fame-rating': 100,
            'location': ['84 Albertina Sisulu Street', 'Johannesburg', 'South Africa'],
            'latlon': ['-24.19436', '29.00974'],
            'age': 42,
            'image_name': 'bob.jpg',
            'gallery': [],
            'token': secrets.token_hex(16),
            'completed': 0,
            'email_confirmed': 1,
            'last-seen': datetime.utcnow(),
            'notifications': []
        }
        db.register_user(Admin)
        print("Admin Created")
