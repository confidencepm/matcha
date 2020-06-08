from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha.utils import login_required, finish_profile
from matcha import db

chatting = Blueprint('chat', __name__)

@chatting.route('/chat')
@login_required
@finish_profile
def chat():
    users = db.users()
    current_user = db.get_user({'username': session.get('username')}, {'matched': 1})
    return render_template('chat/chat.html', logged_in=session.get('username'), users=users, current_user=current_user)


@chatting.route('/room/<room>')
@login_required
@finish_profile
def chat_room(room):
    history = db.get_chat(room)
    chats = []
    
    if not history:
        db.create_history(room)
    else:
        for chat in history['chats']:
            # chats.append(list(chat.values())[0])
            value = (list(chat.values())[0])
            key = list(chat.keys())[0]
            data = list([key, value])
            chats.append(data)

    return render_template('chat/room.html', logged_in=session.get('username'), history=chats, room=room)
