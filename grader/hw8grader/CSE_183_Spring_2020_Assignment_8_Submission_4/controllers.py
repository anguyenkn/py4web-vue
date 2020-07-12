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
import time
from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from .common import db, session, T, cache, auth, signed_url

url_signer = URLSigner(session)


# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    return dict(
        notes_url=URL('notes', signer=url_signer),
        delete_note_url=URL('delete_note', signer=url_signer)
    )


@action('notes', method='GET')
@action.uses(db, session, url_signer.verify())
def notes():
    return dict(notes=db(db.notes.email == auth.current_user.get('email')).select().as_list())


@action('notes', method='POST')
@action.uses(db, session, url_signer.verify())
def notes():
    id = request.json.get('id')
    new_id = db.notes.update_or_insert(db.notes.id == id,
                                       content=request.json.get('content'),
                                       color=request.json.get('color'),
                                       pinned=request.json.get('pinned'),
                                       title=request.json.get('title'),
                                       note_date=request.json.get('note_date'))
    id = id if id else new_id
    return dict(id=id, note_date=db(db.notes.id == id).select().first().note_date)


@action('delete_note', method='POST')
@action.uses(db, session, url_signer.verify())
def notes():
    db((db.notes.id == request.json.get('id')) & (db.notes.email == auth.current_user.get("email"))).delete()
    return 'ok'


################################################
@action('delete_all_notes')
@action.uses(db)
def delete_all_notes():
    """This should be removed before you use the app in production!"""
    db(db.notes).delete()
    return "DELETED ALL"
