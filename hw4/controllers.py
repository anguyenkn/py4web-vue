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
@action('index')
@action.uses('index.html', session, db, auth.user)
def index():
    user_email = auth.current_user.get('email')
    persons = db(db.contact.user_email == user_email).select()
    for person in persons:
        nums = ''
        phones = db(db.phones.contact_id == person.id).select()
        for phone in phones:
            nums += phone.phone + ' (' + phone.kind + '), '
        nums = nums[:-2]
        person['phone_numbers'] = nums
    return dict(persons=persons, url_signer=url_signer, user=auth.user)


@action('add_contact', method=['GET', 'POST'])
@action.uses('add_contact.html', session, auth.user, db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)


@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('add_contact.html', session, auth.user, db)
def edit_contact(contact_id=None):
    user_email = auth.current_user.get('email')
    contact = db.contact[contact_id]
    if contact is None or contact.user_email != user_email:
        redirect(URL('index'))
    form = Form(db.contact, record=contact, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)


@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses(session, auth.user, db, url_signer.verify())
def delete_contact(contact_id=None):
    user_email = auth.current_user.get('email')
    contact = db.contact[contact_id]
    if(contact.user_email == user_email):
        db(db.contact.id == contact_id).delete()
    redirect(URL('index'))


@action('edit_phones/<contact_id>')
@action.uses('edit_phones.html', session, auth.user, db)
def edit_phones(contact_id=None):
    user_email = auth.current_user.get('email')
    if db.contact[contact_id].user_email != user_email:
        redirect(URL('index'))
    rows = db(db.phones.contact_id == contact_id).select()
    contact_name = db.contact[contact_id].first_name + " " + db.contact[contact_id].last_name
    return dict(rows=rows, contact_id=contact_id, contact_name=contact_name, url_signer=url_signer, user=auth.user)


@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', session, auth.user, db)
def add_phone(contact_id=None):
    user_email = auth.current_user.get('email')
    if db.contact[contact_id].user_email != user_email:
        redirect(URL('index'))
    form = Form([
            Field('phone', requires=IS_NOT_EMPTY()),
            Field('kind', requires=IS_NOT_EMPTY())
        ],
        deletable=False,
        csrf_session=session,
        formstyle=FormStyleBulma)
    contact_name = db.contact[contact_id].first_name + " " + db.contact[contact_id].last_name
    if form.accepted:
        phone_input = form.vars['phone']
        kind_input = form.vars['kind']
        db.phones.insert(phone=phone_input, kind=kind_input, contact_id=contact_id)
        redirect(URL('edit_phones', contact_id))
    return dict(contact_name=contact_name, form=form)


@action('edit_phone/<contact_id>/<id>', method=['GET', 'POST'])
@action.uses('add_phone.html', session, auth.user, db)
def edit_phone(contact_id=None, id=None):
    user_email = auth.current_user.get('email')
    if db.contact[contact_id].user_email != user_email:
        redirect(URL('index'))
    phone_entry = db.phones[id]
    form = Form(db.phones, record=phone_entry, deletable=False,csrf_session=session, formstyle=FormStyleBulma)
    contact_name = db.contact[contact_id].first_name + " " + db.contact[contact_id].last_name

    if form.accepted:
        redirect(URL('edit_phones', contact_id))
    return dict(contact_name=contact_name, form=form)


@action('delete_phone/<contact_id>/<id>', method=['GET', 'POST'])
@action.uses(session, auth.user, db, url_signer.verify())
def delete_phone(contact_id=None, id=None):
    user_email = auth.current_user.get('email')
    phone_entry = db.phones[id]
    if db.contact[contact_id].user_email != user_email:
        redirect(URL('index'))
    db(db.phones.id == id).delete()
    redirect(URL('edit_phones', contact_id))