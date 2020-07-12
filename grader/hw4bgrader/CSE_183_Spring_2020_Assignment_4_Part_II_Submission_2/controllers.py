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

# The auth.user below forces login.
@action('index')
@action.uses(auth.user, session, db, url_signer,'index.html')
def index():
    # variable for selecting only the users contacts
    user_email = auth.current_user.get('email')

    contacts = db(db.contact.user_email == user_email).select()

    for contact in contacts:
        phones = db(db.phone.contact_id == contact.id).select()
        phones_string = ""
        phoneList = []
        for phone in phones:
            phoneList.append("{0} ({1})".format(phone.number, phone.kind) )
        phones_string = ", ".join(phoneList)
        contact["phone_numbers"] = phones_string

    return dict(contact_list=contacts, signer=url_signer)

#CONTACT VALIDATION (no None)
def validate_contact(form):
    firstN = form.vars['first_name']
    lastN = form.vars['last_name']
    if firstN is None:
        form.errors['first_name'] = T('Enter your First Name')
    if lastN is None:
        form.errors['last_name'] = T('Enter your Last Name')

@action('add_contact', method=['GET', 'POST'])
@action.uses('add_contact.html', db, session)
def addContact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma, validation=validate_contact)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

#edit contact route
@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('add_contact.html', auth.user, session, db)
def edit_contact(contact_id=None):
    """ contact_id argument must match <contact_id> of @action."""
    user = auth.current_user.get('email')
    expected = db.contact[contact_id].user_email
    contact = db.contact[contact_id]

    if contact_id is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    if expected != user:
        # a different user is trying to edit your contact
        redirect(URL('index'))

    form = Form(db.contact, record=contact, deletable=False,
                csrf_session=session, formstyle=FormStyleBulma, validation=validate_contact)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form, user=user)

# Delete contact route
#  del button uses signed url
@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('index.html', db, session, url_signer.verify())
def delete_contact(contact_id=None):
    user = auth.current_user.get('email')
    e = db.contact[contact_id].user_email

    if e != user:
        redirect(URL('index'))
    c = db.contact[contact_id]
    if c is None:
        redirect(URL('index'))

    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

def validate_phone(form):
    phone = form.vars['number']
    kind = form.vars['kind']
    if phone is None:
        form.errors['number'] = T('Enter a phone number')
    if kind is None:
        form.errors['kind'] = T('Enter a phone kind')

# edit phone route
@action('edit_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('edit_phone.html', db, session, auth)
def edit_phone(contact_id=None):
    user = auth.current_user.get('email')
    expected = db.contact[contact_id].user_email
    contact = db(db.contact.id == contact_id).select()[0]
    phones = db(db.phone.contact_id == contact_id).select()

    if contact_id is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    if expected != user:
        # a different user is trying to edit your contact
        redirect(URL('index'))

    return dict( user=user, phone_list=phones,
                 contact_id=contact_id, signer=url_signer,
                 name=contact.first_name + " " + contact.last_name)

@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', db, session)
def addPhone(contact_id=None):
    contact = db(db.contact.id == contact_id).select()[0]

    form = Form(db.phone , csrf_session=session, formstyle=FormStyleBulma, validation=validate_phone)
    if form.accepted:
        phoneID= form.vars['id']
        db(db.phone.id == phoneID).update(contact_id=contact_id)

        redirect(URL('edit_phone',contact_id))
    return dict(form=form, contact_id=contact_id,
                name=contact.first_name + " " + contact.last_name)


@action('delete_phone_number/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('index.html', db, session, url_signer.verify())
def del_phone_num(contact_id=None, phone_id=None):
    user = auth.current_user.get('email')
    e = db.contact[contact_id].user_email

    if e != user:
        redirect(URL('index'))
    p = db.phone[phone_id]
    if p is None:
        redirect(URL('edit_phones',contact_id))

    db(db.phone.id == phone_id).delete()
    redirect(URL('edit_phone',contact_id))

    
@action('edit_phone_number/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', auth.user, session, db)
def edit_phone_num(contact_id=None, phone_id=None):
    user = auth.current_user.get('email')
    e = db.contact[contact_id].user_email

    if contact_id is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    if e != user:
        # a different user is trying to edit your phone number
        redirect(URL('index'))
    
    contact = db(db.contact.id == contact_id).select()[0]
    phoneNum = db.phone[phone_id]
    form = Form(db.phone, record=phoneNum, deletable=False,
                csrf_session=session, formstyle=FormStyleBulma, validation=validate_phone)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form, user=user, name=contact.first_name + " " + contact.last_name)