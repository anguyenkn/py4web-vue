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
from . models import get_user_email, get_user_first_name, get_user_last_name

url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        # Add other callbacks here.
        user_email = get_user_email(),
        user_first_name = get_user_first_name(),
        user_last_name = get_user_last_name(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name"),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer), 
        get_rating_url = URL('get_rating', signer=url_signer), 
        set_rating_url = URL('set_rating', signer=url_signer),
        get_post_ratings_url = URL('get_post_ratings', signer=url_signer), 
        get_first_last_name_url = URL('get_first_last_name', signer=url_signer)
    )

@action('add_post', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def add_post():
    id = db.post.insert(
            user_email = request.json.get('user_email'),
            post_text = request.json.get('post_text')
        )
        
    return dict(id=id)
    
@action('delete_post', method='POST')
@action.uses(url_signer.verify(), db)
def delete_post():
    id=request.json.get('id')
    if id is not None:
        db(db.post.id == id).delete()
        db(db.thumb.post_id == id).delete()
        return "ok"

@action('get_posts')
@action.uses(url_signer.verify(), auth.user)
def get_posts():
    posts = db(db.post).select(orderby=~db.post.ts).as_list()
    for post in posts:
        user=db(db.auth_user.email == post['user_email']).select().first()
        post['user_first_name']=user.first_name
        post['user_last_name']=user.last_name
    return dict(posts=posts)


@action('get_rating')
@action.uses(url_signer.verify(), db, auth.user)
def like_post():
    post_id = request.params.get('post_id')
    user_email = auth.current_user.get('email')
    assert post_id is not None and user_email is not None
    thumb = db((db.thumb.post_id == post_id) &
                (db.thumb.user_email == user_email)).select().first()
    rating = 0 if thumb is None else thumb.rating
    return dict(rating=rating)

@action('get_post_ratings')
@action.uses(url_signer.verify(), db, auth.user)
def get_post_ratings():
    post_id = request.params.get('post_id')
    assert post_id is not None
    ratings = db(db.thumb.post_id == post_id).select().as_list()
    return dict(ratings = ratings)
    
@action('get_first_last_name')
@action.uses(url_signer.verify(), db, auth.user)
def get_full_name():
    email = request.params.get('user_email')
    assert email is not None
    user = db(db.auth_user.email == email).select().first()
    first = user.first_name
    last = user.last_name
    return dict(name=first+" "+last)

@action('set_rating', method="POST")
@action.uses(db, url_signer.verify(), auth.user)
def set_rating():
    post_id = request.json.get('post_id')
    user_email = auth.current_user.get("email")
    rating = request.json.get('rating')
    assert post_id is not None and rating is not None
    db.thumb.update_or_insert(
        ((db.thumb.post_id == post_id) & (db.thumb.user_email == user_email)), 
        post_id = post_id, 
        user_email = user_email, 
        rating = rating
    )
    return "ok"



# Complete.