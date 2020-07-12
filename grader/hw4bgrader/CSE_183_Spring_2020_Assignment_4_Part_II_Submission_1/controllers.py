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


url_signer = URLSigner(session)

def check_contact_fields(form):
    if not form.errors:
        if form.vars["first_name"] == None:
            form.errors["first_name"]=T("Please enter a first name")
        if form.vars['last_name'] == None:
            form.errors['last_name'] = T("Please enter a last name")
            
def check_phone_fields(form):
    if not form.errors:
        if form.vars['number'] == None:
            form.errors['number'] = T("please enter a phone number")
        if form.vars['phone_name'] == None:
            form.errors['phone_name'] = T("please enter a phone kind")

# The auth.user below forces login.
@action('index')
@action.uses('index.html', auth.user, db, session)
def index():
    rows = db(db.contacts.creator_email == auth.current_user.get('email')
                ).select(db.contacts.ALL)
    phone_rows = db(db.phones.creator_email == auth.current_user.get('email')
                ).select(db.phones.ALL)
    return dict(rows=rows, phone_rows=phone_rows, url_signer=url_signer)

@action('add_contact', method=['GET', 'POST'])
@action.uses('new_contact.html', session, auth.user, db)
def add_contact():
    form = Form(db.contacts, csrf_session=session, 
                formstyle=FormStyleBulma, validation=check_contact_fields)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form, url_signer=url_signer)


@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses(session, db)
def delete_product(contact_id=None):
    p = db.contacts[contact_id]
    if p is None:
        redirect(URL('index'))
    else:
        db(db.contacts.id == contact_id).delete()
        redirect(URL('index'))
    return dict(rows=rows, url_signer=url_signer)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('new_contact.html', session, db)
def edit_product(contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.contacts[contact_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    form = Form(db.contacts, record=p, deletable=False, csrf_session=session, 
                    formstyle=FormStyleBulma, validation=check_contact_fields)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form, url_signer=url_signer)

@action('phones_list/<contact_id>', method=['GET', 'POST'])
@action.uses('contact_phones.html', session, db)
def phones_list(contact_id=None):
    p = db.contacts[contact_id]
    if  p is None:
        redirect(URL('index'))
    rows = db(db.phones.creator_email == auth.current_user.get('email')
                ).select(db.phones.ALL)
    return dict(rows=rows, contact=p, url_signer=url_signer)
    
@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('add_number.html', session, db)
def add_phone(contact_id=None):
    form = Form(db.phones, csrf_session=session, 
                formstyle=FormStyleBulma, validation=check_phone_fields)
    if form.accepted:
        number_id = form.vars['id']
        db(db.phones.id==str(number_id)).update(contact_id=contact_id)
        redirect(URL('phones_list', contact_id))
    return dict(form=form, url_signer=url_signer)

@action('delete_phone/<phone_id>', method=['GET', 'POST'])
@action.uses(session, db)
def delete_phone(phone_id=None):
    p=db.phones[phone_id]
    if p is None:
        redirect(URL('index/'))
    else:
        contact_id = p.contact_id
        db(db.phones.id == phone_id).delete()
        redirect(URL('phones_list/', contact_id))
    return dict(rows=rows, url_signer=url_signer)

@action('edit_phone/<phone_id>', method=['GET', 'POST'])
@action.uses('add_number.html', session, db)
def edit_product(phone_id=None):
    # We read the product.
    p = db.phones[phone_id]
    if p is None:
        redirect(URL('index'))
    form = Form(db.phones, record=p, deletable=False, csrf_session=session, 
                    formstyle=FormStyleBulma, validation=check_phone_fields)
    if form.accepted:
        contact_id = p.contact_id
        redirect(URL('phones_list/', contact_id))
    return dict(form=form, url_signer=url_signer)





















