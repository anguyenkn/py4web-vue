"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior

// CODE ADAPTED FROM TA SESSION: Matan Broner 5/11 5/12 

"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . models import get_user_email

url_signer = URLSigner(session)


# get the name of the logged in user
def fetch_name(email):
    user = db(db.auth_user.email == email).select().first()
    name = user.first_name + " " + user.last_name if user is not None else "Unknown"
    return name

# get the author of the post specified
def fetch_post_author(post_id):
    post = db.post[post_id]
    name = fetch_name(post.user_email)
    return name

# get the likes and dislikes status of the post specified
def fetch_post_thumbs(post_id):
    thumbs = db(db.thumb.post_id == post_id).select().as_list()
    for thumb in thumbs:
        thumb["name"] = fetch_name(thumb["user_email"])
    return thumbs


# get the respective variables to display the post info
def format_post(post_id):
    post = db.post[post_id].as_dict()
    post["author"] = fetch_post_author(post_id)
    post["thumbs"] = fetch_post_thumbs(post_id)
    return post




# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        thumb_post_url = URL('thumb_post', signer=url_signer),

        # Add other callbacks here.
        user_email = get_user_email(),
        user = auth.user,
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user, db)
def get_posts():
    # Complete.
    posts = db().select(db.post.ALL, orderby=~db.post.ts).as_list()
    formatted_posts = []
    for post in posts:
        formatted_posts.append(format_post(post["id"]))
    return dict(posts=formatted_posts)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def add_post():
    # Complete.
    post_text = request.json.get('post_text')
    new_id = db.post.insert(post_text=post_text)
    post = db.post[new_id]
    post = format_post(post.id)
    return dict(post=post) # You need to fill this in. 

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def delete_post():
    # Complete.
    post_id = request.json.get('post_id')
    if post_id is not None:
        db(db.post.id == post_id).delete()
    return dict() # You need to fill this in.

@action('thumb_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def thumb_post():
    # Complete.
    post_id = request.json.get('post_id')
    rating = request.json.get('rating')
    user_email = auth.current_user.get("email")
    db.thumb.update_or_insert(
        (db.thumb.post_id == post_id) & (db.thumb.user_email == user_email),
        rating=rating,
        post_id=post_id,
        user_email=user_email
    )
    post = format_post(post_id)
    return dict(post=post) # You need to fill this in.

# Complete.