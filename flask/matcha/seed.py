from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha import db, logged_in_users
from bson import ObjectId
from functools import wraps
import secrets, re, bcrypt, html
from matcha.utils import *
from faker import Faker
import random
from datetime import datetime

def seed_users():
    n = 50 #number of users you want to create
    fake = Faker()
    gender = ['Male', 'Female']
    sexo = ['bisexual', 'heterosexual', 'homosexual']
    interests = ['Animals', 'Cheaters', 'Lookingforlove', 'Quickie', 'Travel', 'Menaretrash', 'NSA', 'Trans', 'LFF']
    profile_pics = ['dummy1.png', 'dummy2.png', 'dummy3.png', 'dummy4.png', 'dummy5.png', 'dummy6.png', 'dummy7.png', 'dummy8.png', 'dummy9.png', 'dummy10.png'] 
    
    #create a dictionary for 50 randon users
    for _ in range(n):
       
        salt = bcrypt.gensalt()
        details = {
            'username' : '',
            'firstname' : '',
            'lastname' : '',
            'email' : 'cmcmukwindidza26@gmail.com',
            'password' : bcrypt.hashpw('Password1'.encode('utf-8'), salt),
            'gender': '',
            'sex': 'bisexual',
            'bio': '',
            'interests': [],
            'flirts' : [],      
            'flirted' : [],     
            'matched' : [],
            'blocked' : [],     
            'views' : [],
            'rooms': {},
            'fame-rating': 0,
            'location': [],
            'latlon' : '',
            'age': 18,
            'image_name': 'dummy1.png',
            'gallery': [],
            'token': secrets.token_hex(16),
            'completed': 1,
            'email_confirmed': 1,
            'last-seen': datetime.utcnow(),
            'notifications': []
        }
        #load the 50 created users with random/fake data.
        details['username'] = fake.user_name()
        details['firstname'] = fake.first_name()
        details['lastname'] = fake.last_name()
        details['gender'] = random.choice(gender)
        details['sex'] = random.choice(sexo)
        details['bio'] = fake.text()
        num = fake.random_int(2,6)
        details['interests'] = random.sample(interests, num)
        details['fame-rating'] = fake.random_int(0, 80)
        details['location'].append(''.join([str(fake.random_int(1,500)), ' ', fake.word(), ' street']))
        details['location'].append(''.join([fake.word(),'cliff']))
        details['location'].append(fake.city())
        details['location'].append('South Africa')
        details['latlon'] = fake.local_latlng(country_code="ZA", coords_only=True)
        details['age'] = fake.random_int(18,80)
        details['image_name'] = random.choice(profile_pics)
        
        db.register_user(details)
        # register fake users in an sql database
        db.re
    message = str(n) + ' users created'
    print(message)
    if not db.get_user({'username': "Bobbers"}, {'username': 1}):
        salt = bcrypt.gensalt()
        Admin = {
            '_id' : ObjectId(b'bobisadmin!!'),
            'username' : 'Bobbers',
            'firstname' : 'Bob',
            'lastname' : 'Admin',
            'email' : 'cmcmukwindidza26@gmail.com',
            'password' : bcrypt.hashpw('Password1'.encode('utf-8'), salt),
            'gender': 'Female',
            'sex': 'bisexual',
            'bio': 'Hi my name is Bob, I am the greatest, duh',
            'interests': ['Nothin', 'fokol'],
            'flirts' : [],      
            'flirted' : [],     
            'matched' : [],
            'blocked' : [],     
            'views' : [],
            'rooms': {},
            'fame-rating': 100,
            'location': ['1 Thegreatest Street', 'Greatnesscliff', 'Bobberg', 'South Africa'],
            'latlon' : ['-24.19436','29.00974'],
            'age': 42,
            'image_name': 'bob.jpg',
            'gallery': [],
            'token': secrets.token_hex(16),
            'completed': 1,
            'email_confirmed': 1,
            'last-seen': datetime.utcnow(),
            'notifications': [] 
        }
        db.register_user(Admin)
        print("Admin Created")
