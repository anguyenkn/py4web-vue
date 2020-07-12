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
from pydal.validators import *


url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index', method='GET')
@action.uses('index.html', auth, auth.user, session, db)
def index():
    user = auth.get_user()
    # Get contacts as a list using as_l.
    rows = db(db.person.user_email == auth.current_user.get('email')).select().as_list()
    for row in rows:
        phone_rows = db(db.phone.person_id == row['id']).select().as_list()
        s = ''
        for phone_row in phone_rows:
            s += phone_row['phone'] + ' (' + phone_row['kind'] + ')'
            if phone_row != phone_rows[-1]:
                s += ', '
        row['phone_numbers'] = s
    return dict(user=user, rows=rows, signed_url=signed_url)

@action('add_contact', method=['GET', 'POST'])
@action.uses('contact_form.html', auth, auth.user, session, db)
def add_contact():
    user = auth.get_user()
    form = Form(db.person, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(user=user, form=form)

@action('edit_contact/<person_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', auth, auth.user, session, db)
def edit_contact(person_id=None):
    user = auth.get_user()
    # We read the contact.
    p = db.person[person_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif p.user_email != auth.current_user.get('email'):
        # If entry exists but doesn't belong to the user, redirect, as the edit is not allowed.
        redirect(URL('index'))
    
    form = Form(db.person, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(user=user, form=form)

@action('delete_contact/<person_id>', method=['GET', 'POST'])
@action.uses('index.html', auth, auth.user, session, db, signed_url.verify())
def delete_contact(person_id=None):
    p = db.person[person_id]
    if p is None:
        # Nothing to delete.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    
    # Only delete the entry if it belongs to the user.
    db((db.person.id == person_id) & (db.person.user_email == auth.current_user.get('email'))).delete()
    redirect(URL('index'))

@action('edit_phones/<person_id>', method='GET')
@action.uses('phone_index.html', auth, auth.user, session, db)
def edit_phones(person_id=None):
    user = auth.get_user()
    # We read the contact.
    p = db.person[person_id]
    if p is None:
        # No person entered.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif p.user_email != auth.current_user.get('email'):
        # If person exists but doesn't belong to the user, redirect.
        redirect(URL('index'))
    
    rows = db(db.phone.person_id == person_id).select()
    return dict(user=user, rows=rows, p=p, signed_url=signed_url)

@action('add_phone/<person_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', auth, auth.user, session, db)
def add_phone(person_id=None):
    user = auth.get_user()
    # We read the contact.
    p = db.person[person_id]
    if p is None:
        # No person to add a phone number to.
        #This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif p.user_email != auth.current_user.get('email'):
        # If person exists but doesn't belong to the user, redirect.
        redirect(URL('index'))
    
    # Verify that the form entries are not left blank.
    form = Form([Field('phone', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        db.phone.insert(person_id=person_id, phone=form.vars['phone'], kind=form.vars['kind'])
        redirect(URL('edit_phones', person_id))
    return dict(user=user, form=form, p=p)

@action('edit_phone/<person_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', auth, auth.user, session, db)
def edit_phone(person_id=None, phone_id=None):
    user = auth.get_user()
    # We read the contact.
    p = db.person[person_id]
    # We read the phone number.
    ph = db.phone[phone_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif ph is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif p.id != ph.person_id or p.user_email != auth.current_user.get('email'):
        # If the number doesn't correspond to the contact, redirect.
        # If the number exists but doesn't belong to the user, redirect.
        # These should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    
    form = Form(db.phone, record=ph, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('edit_phones', person_id))
    return dict(user=user, form=form, p=p)

@action('delete_phone/<person_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('phone_index.html', auth, auth.user, session, db, signed_url.verify())
def delete_phone(person_id=None, phone_id=None):
    # We read the contact.
    p = db.person[person_id]
    # We read the phone number.
    ph = db.phone[phone_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif ph is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    elif p.id != ph.person_id:
        # If the number doesn't correspond to the contact, redirect.
        # This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    
    # Only delete the entry if it belongs to the user.
    db((db.phone.id == phone_id) & (db.phone.user_email == auth.current_user.get('email'))).delete()
    redirect(URL('edit_phones', person_id))