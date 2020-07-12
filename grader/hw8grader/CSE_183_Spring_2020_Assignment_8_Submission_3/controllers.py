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
        get_notes_url = URL('get_notes', signer=url_signer),
        get_shade_url = URL('get_shade', signer=url_signer),
        set_shade_url = URL('set_shade', signer=url_signer),
        get_star_url = URL('get_star', signer=url_signer),
        set_star_url = URL('set_star', signer=url_signer),
        add_note_url = URL('add_note', signer=url_signer),
        save_note_url = URL('save_note', signer=url_signer),
        delete_note_url = URL('delete_note', signer=url_signer),
        user_email = get_user_email(),
    )

@action('get_notes')
@action.uses(url_signer.verify(), auth.user)
def get_notes():
    notes = db(db.note.user_email == auth.current_user.get('email')).select(orderby=~db.note.id).as_list()
    return dict(notes=notes)
    
@action('add_note', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def add_note():
    id = db.note.insert(
        note_text = request.json.get('note_text'),
        note_title = request.json.get('note_title'),
    )
    return dict(id = id)
    
@action('save_note',  method="POST")
@action.uses(db, auth.user)  # etc.  Put here what you need.
def save_note():
    
    note_id = request.json.get('id') # Note: id can be none.
    note_text = request.json.get('note_text')
    note_title = request.json.get('note_title')

    new_id = db.note.update_or_insert(
        db.note.id == note_id,
        note_title = note_title,
        note_text = note_text,
    )
    
    return dict(note_title=note_title, note_text=note_text, id=new_id)
    
@action('delete_note', method="POST")
@action.uses(url_signer.verify(), db)
def delete_note():
    id = request.json.get('id')
    if id is not None:
        db(db.note.id == id).delete()
    return "ok" # Just to return something.
# Complete.
    
@action('get_shade')
@action.uses(url_signer.verify(), db, auth.user)
def get_shade():
    """Returns the rating for a user and an image."""
    note_id = request.params.get('note_id')
    user_id = auth.current_user.get('email')
    assert note_id is not None
    shade_entry = db((db.color.note_id == note_id) &
                      (db.color.user_email == user_id)).select().first()
    shade = shade_entry.shade if shade_entry is not None else 1
    return dict(shade=shade)
    
@action('set_shade', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_shade():
    """Sets the rating for an image."""
    note_id = request.json.get('note_id')
    user_id = auth.current_user.get('email')
    shade = request.json.get('shade')
    assert note_id is not None and shade is not None
    db.color.update_or_insert(
        ((db.color.note_id == note_id) & (db.color.user_email == user_id)),
        note_id=note_id,
        user_email=user_id,
        shade=shade,
    )
    return "ok" # Just to have some confirmation in the Network tab.
    
@action('get_star')
@action.uses(url_signer.verify(), db, auth.user)
def get_star():
    """Returns the rating for a user and an image."""
    note_id = request.params.get('note_id')
    user_id = auth.current_user.get('email')
    assert note_id is not None
    star_entry = db((db.starred.note_id == note_id) &
                      (db.starred.user_email == user_id)).select().first()
    star = star_entry.star if star_entry is not None else 0
    return dict(star=star)
    
@action('set_star', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_star():
    """Sets the rating for an image."""
    note_id = request.json.get('note_id')
    user_id = auth.current_user.get('email')
    star = request.json.get('star')
    assert note_id is not None and star is not None
    db.starred.update_or_insert(
        ((db.starred.note_id == note_id) & (db.starred.user_email == user_id)),
        note_id=note_id,
        user_email=user_id,
        star=star,
    )
    return "ok" # Just to have some confirmation in the Network tab.
