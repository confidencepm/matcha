from flask import render_template, redirect, request, abort, url_for, flash, session, Blueprint
from matcha import db
from functools import wraps
from datetime import datetime
from matcha.utils import *
import html

# Create the blueprint for the posts.
posts = Blueprint('posts', __name__)


# Route for the user posts
@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
# @finish_profile
def new_post():
    user = db.get_user({'username':session.get('username')})
    post = {
        'author': user,
        'title': '',
        'content': '',
        'date_posted': ''
    }

    if request.method == 'POST':
        post['title'] = html.escape(request.form.get('title'))
        post['content'] = html.escape(request.form.get('content'))
        post['date_posted'] = datetime.utcnow()

        db.add_post(post)
        return redirect( url_for('main.home') )
    return render_template('posts/create_post.html', logged_in=session.get('username'))
    

# Route for veiwing the post
@posts.route('/post/<post_id>')
@login_required
@finish_profile
def post(post_id):
    post = db.get_post(post_id)
    post['title'] = html.unescape(request.form.get('title'))
    post['content'] = html.unescape(request.form.get('content'))

    return render_template('posts/post.html', post=post, logged_in=session.get('username'))


# Route for editing the post
@posts.route('/post/<string:post_id>/update', methods=['GET', 'POST'])
@login_required
@finish_profile
def update_post(post_id):
    post = db.get_post(post_id)
    if session.get('username') != post['author']['username']:
        abort(403)
    
    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')

        db.update_post(post)
        return redirect( url_for('posts.post', post_id=post_id))
    return render_template('posts/update_post.html', logged_in=session.get('username'), post=post)

# Route for deleting a single post.
@posts.route('/post/<string:post_id>/delete', methods=['GET', 'POST'])
@login_required
@finish_profile
def delete_post(post_id):
    post = db.get_post(post_id)
    if session.get('username') != post['author']['username']:
        abort(403)
    db.delete_post(post)
    return redirect( url_for('main.home') )

