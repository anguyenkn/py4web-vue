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
        # Add other callbacks here.
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name"),
        get_ratign_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_likers_url = URL('get_likers', signer=url_signer),
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user, db)
def get_posts():
    posts = db(db.post).select(orderby=~db.post.ts).as_list()
    for post in posts:
        post_email = post.get('user_email') if post is not None else ""
        current_user_email = auth.current_user.get('email')
        post_id = post.get('id') if post is not None else ""

        author_entry = db(db.auth_user.email == post_email).select().first()
        author = author_entry.get('first_name') + " " + author_entry.get('last_name')
        post['author'] = author

        rating_entry = db((db.thumb.post_id == post_id) & (db.thumb.user_email == current_user_email)).select().first()
        rating = rating_entry.get('rating') if rating_entry is not None else 0
        post['rating'] = rating
    return dict(posts=posts)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def add_post():
    id = db.post.insert(
        post_text = request.json.get('post_text')
    )
    author = auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')
    return dict(id=id, author=author)

@action('get_likers')
@action.uses(url_signer.verify(), auth.user, db)
def get_likers():
    post_id = request.params.get('post_id')
    liker_string = ""
    disliker_string = ""
    # Likers
    liker_entries = db((db.thumb.post_id == post_id) & (db.thumb.rating == 1)).select(db.thumb.user_email).as_list()
    liker_count = db((db.thumb.post_id == post_id) & (db.thumb.rating == 1)).count()
    for entry in liker_entries:
        author_entry = db(db.auth_user.email == entry.get('user_email')).select().first()
        liker_string += author_entry.get('first_name') + " " + author_entry.get('last_name') + ", "
    liker_string = liker_string[:-2]
    # Dislikers
    disliker_entries = db((db.thumb.post_id == post_id) & (db.thumb.rating == -1)).select(db.thumb.user_email).as_list()
    for entry in disliker_entries:
        author_entry = db(db.auth_user.email == entry.get('user_email')).select().first()
        disliker_string += author_entry.get('first_name') + " " + author_entry.get('last_name') + ", "
    disliker_string = disliker_string[:-2]

    return dict(liker_string=liker_string, disliker_string=disliker_string)

@action('set_rating', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_rating():
    post_id = request.json.get('post_id')
    user_email = auth.current_user.get('email')
    rating = request.json.get('rating')
    db.thumb.update_or_insert(
        ((db.thumb.post_id == post_id) & (db.thumb.user_email == user_email)),
        post_id=post_id,
        user_email = user_email,
        rating=rating
    )
    return "Ok"

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.json.get('id')
    if id is not None:
        db(db.post.id == id).delete()
    return "ok"