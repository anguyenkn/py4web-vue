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
        thumb_post_url = URL('thumb_post', signer=url_signer),
        get_thumbs_url = URL('get_thumbs', signer=url_signer),
        get_username_url = URL('get_username', signer=url_signer),
        # Add other callbacks here.
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user, db)
def get_posts():
    # Complete.
    posts = db(db.post).select(orderby=~db.post.ts).as_list()
    for p in posts:
        # Get post author
        r = db(db.auth_user.email == p['user_email']).select().first()
        p['author'] = r.first_name + " " + r.last_name if r is not None else "Unknown"
        
        # Get whether post was liked or disliked by current user
        r = db((db.thumb.user_email == auth.current_user.get("email")) & (db.thumb.post_id == p['id'])).select()
        if r:
            r = r.first()
        p['liked'] = bool(r and r['rating'] > 0)
        p['disliked'] = bool(r and r['rating'] < 0)
        p['liked_by'] = ''
        p['disliked_by'] = ''
        p['show_likers'] = False
        p['cache_likes'] = False
    return dict(posts=posts)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def add_post():
    id = db.post.insert(
        post_text = request.json.get('new_post_content')
    )
    db.thumb.insert(
        post_id = id
    )
    return dict(id = id)

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def delete_post():
    id = request.json.get('id')
    if id is not None:
        r = db(db.post.id == id)
        if r and r.select().first()['user_email'] == auth.current_user.get('email'):
            r.delete()
            db(db.thumb.post_id == id).delete()
    return {}

@action('thumb_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def thumb_post():
    rating = request.json.get('rating')
    if rating < -1 or rating > 1:
        return {}
    id = request.json.get('id')
    if id is not None:
        r = db((db.thumb.post_id == id) & (db.thumb.user_email == auth.current_user.get('email')))
        if r:
            r.delete()
        db.thumb.insert(
            post_id = id,
            user_email = auth.current_user.get("email"),
            rating = rating
        )
    return {}

@action('get_thumbs', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def get_thumbs():
    id = request.json.get('id')
    rows = db(db.thumb.post_id == id).select()
    liked_list = []
    disliked_list = []
    for r in rows:
        user = db(db.auth_user.email == r.user_email).select().first()
        if r.rating > 0:
            liked_list.append(user.first_name + " " + user.last_name if user else "Unknown")
        if r.rating < 0:
            disliked_list.append(user.first_name + " " + user.last_name if user else "Unknown")
    liked_by = "Liked by " + ','.join(liked_list) if len(liked_list) else ""
    disliked_by = "Disliked by " + ','.join(disliked_list) if len(disliked_list) else ""
    return dict(liked_by = liked_by, disliked_by = disliked_by)

@action('get_username', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def get_username():
    r = db(db.auth_user.email == auth.current_user.get("email")).select().first()
    return dict(username=(r.first_name + " " + r.last_name if r is not None else "Unknown"))