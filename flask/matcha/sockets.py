from matcha import socket, logged_in_users, db
from flask import session, request
from flask_socketio import join_room, leave_room
import secrets
from bson.objectid import ObjectId


@socket.on('connect')
def connect():
    user_name = session.get('username')
    logged_in_users[user_name] = request.sid
    print (user_name, 'connected: id -',logged_in_users[user_name])



@socket.on('disconnect')
def disconnect():
    logged_in_users[session.get('username')] = ''


@socket.on('flirt')
def flirt(data):
    flirter = db.get_user({'username': session.get('username')}, {'username': 1, 'flirts': 1})
    flirtee = db.get_user({'username': data['to']}, {'username':1, 'flirted': 1})

    print('flirter', flirter['username'])
    print('flirtee', flirtee['username'])

    flirter['flirts'].append(flirtee['username'])
    flirtee['flirted'].append(flirter['username'])


    print('flirter:', flirter['flirts'])
    print('flirtee:', flirtee['flirted'])

    db.update_flirts(flirter['_id'], {'flirts': flirter['flirts']})
    db.update_flirts(flirtee['_id'], {'flirted': flirtee['flirted']})

    sid = logged_in_users.get(data['to'])
    if sid:
        socket.emit('flirt', {'from': session.get('username')}, room=sid)
        
    flirtee['notifications'].append(session.get('username') + ' has sent you a message')
    db.update_flirts(flirtee['_id'], {'notifications' : flirtee['notifications']})


@socket.on('flirt-back')
def flirt_back(data):
    flirt_back = db.get_user({'username': session.get('username')}, {'username':1, 'flirts' : 1, 'matched': 1, 'rooms': 1})
    flirtee = db.get_user({'username' :data['to']}, {'username' : 1, 'flirted' : 1, 'matched' :1, 'rooms': 1})
    room = secrets.token_hex(16)

    flirt_back['flirts'].append(flirtee['username'])
    flirtee['flirted'].append(flirt_back['username'])
    # add to the matched array.
    flirt_back['matched'].append(flirtee['username'])
    flirtee['matched'].append(flirt_back['username'])
    # add a unique room to this twos matched
    flirt_back['rooms'][flirtee['username']] = room
    flirtee['rooms'][flirt_back['username']] = room

    db.update_flirts(flirt_back['_id'], {'flirts': flirt_back['flirts'], 'matched': flirt_back['matched'], 'rooms': flirt_back['rooms']})
    db.update_flirts(flirtee['_id'], {'flirted': flirtee['flirted'], 'matched': flirtee['matched'], 'rooms': flirtee['rooms']})

    sid = logged_in_users.get(data['to'])
    if sid:
        socket.emit('matched', {'from' : session.get('username')}, room=sid)

    flirtee['notifications'].append(session.get('username') + ' has flirted')
    db.update_flirts(flirtee['_id'], {'notifications' : flirtee['notifications']})

    print(data)

@socket.on('Unlike')
def unlike(data):
    print(data['to'], 'has been unliked.')
    current_user = db.get_user({'username': session.get('username')}, {'flirts': 1, 'matched': 1})
    unlikes = db.get_user({'username': data['to']}, {'flirted': 1, 'matched': 1, 'notifications': 1})

    print('unlikes ', unlikes)
    if data['to'] in current_user['flirts']:
        current_user['flirts'].remove(data['to'])
        unlikes['flirted'].remove(session.get('username'))
    if current_user['matched'] and data['to'] in current_user['matched']:
        current_user['matched'].remove(data['to'])
        unlikes['matched'].remove(session.get('username'))
    
    db.update_flirts(current_user['_id'], {'flirts': current_user['flirts'], 'matched': current_user['matched']})
    db.update_flirts(unlikes['_id'], {'flirted': unlikes['flirted'], 'matched': unlikes['matched']})

    sid = logged_in_users[data['to']]
    if sid:
        socket.emit('Unlike', {'from': session.get('username')}, room=sid)
    
    unlikes['notifications'].append(session.get('username') + ' has unliked you.')
    db.update_flirts(unlikes['_id'], {'notifications': unlikes['notifications']})

def join(data):
    join_room(data)

@socket.on('leave')
def leave(data):
    leave_room(data)

@socket.on('send')
def send(data):
    users = db.users()
    current_user = db.get_user({'username': session.get('username')}, {'_id': 1})
    notif_to = None

    for user in users:
        if data['room'] in user['rooms'].values() and not user['username'] == session.get('username'):
            notif_to = user
            break

    
    if current_user['_id'] in user['blocked']:
        return False


    db.insert_chat(data['from'], data['room'], data['message'])
    socket.emit('recieve', {'from': data['from'], 'message': data['message']}, include_self=False, room=data['room'])
    socket.emit('notif_chat', {'from': data['from'], 'message':data['message']}, sid=logged_in_users[notif_to['username']])
    if not notif_to['username'] in logged_in_users:
        notif_to['notifications'].append(session.get('username') + ' has sent you a message')
        db.update_flirts(notif_to['_id'], {'notifications' : notif_to['notifications']})


@socket.on('view')
def view_user_profile(data):
    print('recieving the data')
    viewed_user = db.get_user({'_id': ObjectId(data['viewed'])})
    viewer =  db.get_user({'_id': ObjectId(data['viewer'])}, {'username' : 1})

    print(viewed_user['username'])
    if data['viewer'] in viewed_user['views'] or viewer['_id'] in viewed_user['blocked']:
        return False
    
    if viewed_user['username'] in logged_in_users:
        print(data['viewed'], ' is online')
        socket.emit('notif_view', {'from': viewer['username']}, sid=logged_in_users[viewed_user['username']])
        
    viewed_user['notifications'].append(viewer['username'] + ' has viewed you profile')

    viewed_user['views'].append(data['viewer'])
    db.update_flirts(viewed_user['_id'], {'views': viewed_user['views'], 'notifications': viewed_user['notifications']})

    print(data)


@socket.on('read')
def read(data):
    print('notifications read')
    user = db.get_user({'username': session.get('username')}, {'notifications': 1})
    user['notifications'] = []
    db.update_flirts(user['_id'], {'notifications': user['notifications']})
