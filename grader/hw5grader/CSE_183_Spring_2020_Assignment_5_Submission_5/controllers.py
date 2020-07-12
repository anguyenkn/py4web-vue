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
"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . models import get_user_email

url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name"),
        like_post_url = URL('like_post', signer=url_signer),
        dislike_post_url = URL('dislike_post', signer=url_signer),
        get_thumbs_url = URL('get_thumbs')
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user)
def get_posts():
    posts = db(db.post).select().as_list()
    thumbs = db(db.thumb).select().as_list()
    for post in posts:
        r = db(db.auth_user.email == auth.current_user.get("email")).select().first()
        name = r.first_name + " " + r.last_name if r is not None else "Unknown"
        post['name'] = name
    for thumb in thumbs:
        r = db(db.auth_user.email == thumb['user_email']).select().first()
        name = r.first_name + " " + r.last_name if r is not None else "Unknown"
        thumb['name'] = name
    return dict(posts=posts, thumbs=thumbs)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user)
def add_post():
    id = db.post.insert(
        post_text = request.json.get('post_contents')
    )
    r = db(db.auth_user.email == auth.current_user.get("email")).select().first()
    name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    return dict(id=id, name=name)

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), auth.user)
def delete_post():
    post = db.post[int(request.json.get("post_id"))]
    stop = auth.current_user.get('email') != post.user_email or post is None
    deleted = 0
    if not stop:
        db(db.post.id == post.id).delete()
        deleted = 1
    return dict(deleted=deleted)

@action('like_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def like_post():
    post_id = request.json.get("post_id")
    rating = 0
    print(post_id)
    thumbs = db(db.thumb).select().as_list()
    thumb = None
    for t in thumbs:
        if t["post_id"] == post_id and t["user_email"] == auth.current_user.get("email"):
            thumb = t

    if thumb is None:
        print("no rating")
        rating = db.thumb.insert(
            post_id = post_id,
            rating = 1
        )
    else:
        thumb = db(db.thumb.id == thumb["id"]).select().first()
        if thumb.rating == 1:
            print("rating is 1")
            thumb.update_record(rating=0)
        else:
            print("rating is not 1")
            thumb.update_record(rating=1)
            rating = 1

    print(db(db.thumb).select())
    r = db(db.auth_user.email == auth.current_user.get("email")).select().first()
    name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    return dict(rating=rating, name=name)

@action('dislike_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def dislike_post():
    post_id = request.json.get("post_id")
    rating = 0
    print(post_id)
    thumbs = db(db.thumb).select().as_list()
    thumb = None
    for t in thumbs:
        if t["post_id"] == post_id and t["user_email"] == auth.current_user.get("email"):
            thumb = t

    if thumb is None:
        print("no rating")
        rating = db.thumb.insert(
            post_id = post_id,
            rating = -1
        )
    else:
        thumb = db(db.thumb.id == thumb["id"]).select().first()
        if thumb.rating == -1:
            print("rating is -1")
            thumb.update_record(rating=0)
        else:
            print("rating is not -1")
            thumb.update_record(rating=-1)
            rating = -1

    print(db(db.thumb).select())
    r = db(db.auth_user.email == auth.current_user.get("email")).select().first()
    name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    return dict(rating=rating, name=name)

@action('get_thumbs')
@action.uses(db)
def get_thumbs():
    thumbs = db(db.thumb).select().as_list()
    for thumb in thumbs:
        r = db(db.auth_user.email == thumb['user_email']).select().first()
        name = r.first_name + " " + r.last_name if r is not None else "Unknown"
        thumb['name'] = name
    return dict(thumbs=thumbs)

# Complete.