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

import random
import time
import uuid
import datetime
from os.path import join as pjoin
import shutil

from py4web import action, request, abort, redirect, URL, Field, HTTP
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url

def get_time():
    return datetime.datetime.utcnow()

url_signer = URLSigner(session)

def get_name_from_email(e):
    """Given the email of a user, returns the name."""
    u = db(db.auth_user.email == e).select().first()
    return "" if u is None else u.first_name + " " + u.last_name


# The auth.user below forces login.
@action('index')
@action.uses(auth.user, url_signer, session, db, 'index.html')
def index():
    return dict(
        notes_url = URL('notes', signer=url_signer),
        upload_url = URL('file_upload', signer=url_signer),
        delete_url = URL('delete_note', signer=url_signer),
        color_url = URL('change_note_value', signer=url_signer),
        user_email = auth.current_user.get('email'),
        author_name = auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')
     )


@action('notes', method="GET")
@action.uses(db, auth.user, session, url_signer.verify())
def get_notes():
    user_email = auth.current_user.get('email')
    notes = []
    all_notes = db(db.notes).select().as_list()
    # Filtering
    for note in all_notes:
        if note.get('email') == user_email:
            notes.append(note)
        elif note.get('shared_email') != None:
            if note.get('shared_email').lower().find(user_email) != -1:
                notes.append(note)
            elif note.get('shared_email').lower().find('everyone') != -1:
                notes.append(note)
    return dict(notes=notes)


@action('notes',  method="POST")
@action.uses(db, auth.user)
def save_post():
    paramID = request.json.get('id')
    content = request.json.get('content')
    title = request.json.get('title')
    color = request.json.get('color')
    last_modified = get_time()
    image_url = request.json.get('image_url')
    shared_email = request.json.get('shared_email')
    id = db.notes.update_or_insert(
        (db.notes.id == paramID),
        content = content,
        title = title,
        color = color,
        last_modified = last_modified,
        image_url = image_url,
        shared_email = shared_email,
    )
    id = paramID if id == None else id
    return dict(content=content, id=id, title=title, last_modified=last_modified, shared_email=shared_email)


@action('delete_note',  method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
def delete_note():
    db(db.notes.id == request.json.get('id')).delete()
    return "ok"


@action('delete_all_posts')
@action.uses(db)
def delete_all_posts():
    """This should be removed before you use the app in production!"""
    db(db.post).delete()
    return "ok"


@action('change_note_value',  method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
def change_note_value():
    color = request.json.get('color')
    star = request.json.get('star')
    last_modified = get_time()
    db(db.notes.id == request.json.get('id')).update(
        color = color,
        star = star,
        last_modified = last_modified,
    )
    return dict(last_modified=last_modified)

@action('file_upload',  method="POST")
def file_upload():
        file = request.files.get('file')
        id = request.headers.get('id')
        last_modified = get_time()
        if file is None:
            print("No file")
        else:
            file_path = pjoin("apps", "hw8", "static", "images", "notes", file.filename)
            new_file = open(file_path, "wb")
            new_file.write(file.file.read())
            print("Saved file")
            image_url = pjoin("..", "static", "images", "notes", file.filename) 
            db(db.notes.id == id).update(image_url=image_url, last_modified=last_modified)
            return dict(image_url=image_url, last_modified=last_modified)