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
from pydal.validators import *

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url


url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', auth.user, db)
def index():
    rows = db(db.contact.user_email==auth.current_user.get('email')).select()
    rowNumbers=[]
    for row in rows:
        nums = db(db.phone.phone_user==row.id).select()
        numberString = ""
        for num in nums:
            numberString += (num.number + " (" + num.kind + ")")
            if num != nums[-1]:
                numberString += ", "
        rowNumbers.append (numberString)
    return dict(rows=rows, rowNumbers=rowNumbers, url_signer=signed_url)


@action('add_contact', method=['GET', 'POST'])
@action.uses('add_contact.html', session, db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('add_contact.html', session, db)
def edit_contact(contact_id=None):
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=p.get('user_email')):
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('index.html', session, db, url_signer.verify())
def delete_contact(contact_id=None):
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=p.get('user_email')):
        redirect(URL('index'))
    else:
        db(db.contact.id == contact_id).delete()
        redirect(URL('index'))

#-------------------------------------------------------------------------------------------------------------

@action('edit_phones/<contact_id>')
@action.uses('edit_phones.html', auth.user, db)
def edit_phones(contact_id=None):
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=p.get('user_email')):
        redirect(URL('index'))
    rows = db(db.phone.phone_user==contact_id).select()
    return dict(contact_id=contact_id, person=p, rows=rows, url_signer=signed_url)

@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', session, db)
def add_phone(contact_id=None):
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=p.get('user_email')):
        redirect(URL('index'))
    form = Form([Field('number', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        db.phone.insert(number = form.vars["number"], kind = form.vars["kind"], phone_user = contact_id)
        redirect(URL('edit_phones', contact_id))
    return dict(person=p, form=form)

@action('edit_phone/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', session, db)
def edit_phone(contact_id=None, phone_id=None):
    p = db.phone[phone_id]
    if p is None:
        redirect(URL('index'))
    c = db.contact[contact_id]
    if c is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=c.get('user_email')):
        redirect(URL('index'))
    form = Form(db.phone, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('edit_phones', contact_id))
    return dict(person=c, form=form)

@action('delete_phone/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('edit_phones.html', session, db, url_signer.verify())
def delete_phone(contact_id=None, phone_id=None):
    p = db.phone[phone_id]
    if p is None:
        redirect(URL('index'))
    c = db.contact[contact_id]
    if c is None:
        redirect(URL('index'))
    if (auth.current_user.get('email')!=c.get('user_email')):
        redirect(URL('index'))
    else:
        db(db.phone.id == phone_id).delete()
        redirect(URL('edit_phones', contact_id))