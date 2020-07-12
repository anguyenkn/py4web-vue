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
@action.uses('index.html', auth.user, db)
def index():
    email = auth.current_user.get('email')
    rows = db(db.contact.user_email == email).select()
    phones = db(db.phone).select()
    return dict(url_signer=url_signer,rows=rows,phones = phones)

@action('add_contact', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db)
def edit_contact(contact_id = None):
    p = db.contact[contact_id]
    row = db(db.contact.id == p).select().first()
    email = auth.current_user.get('email')
    if p is None:
        redirect(URL('index'))
    if p is not None:
        if row.user_email == email:
            form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma, record=p,deletable=False)
            if form.accepted:
                redirect(URL('index'))
            return dict(form=form)
        else:
            redirect(URL('index'))

@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db,url_signer.verify())
def delete_contact(contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <contact_id> argument of the @action."""
    # We read the product.
    p = db.contact[contact_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    if p is not None:
        db(db.contact.id == p).delete()
        redirect(URL('index'))

@action('edit_phones/<contact_id>', method=['GET', 'POST'])
@action.uses('edit_phones.html',session, db)
def edit_phones(contact_id = None):
    p = db.contact[contact_id]
    row = db(db.contact.id == p).select().first()
    numbers = db(db.phone.contact_id == p).select()
    email = auth.current_user.get('email')
    if p is None:
        redirect(URL('index'))
    if p is not None:
        if row.user_email == email:
            return dict(row=row, numbers=numbers,url_signer=url_signer)
        else:
            redirect(URL('index'))

@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', session, db)
def add_phone(contact_id = None):
    p = db.contact[contact_id]
    row = db(db.contact.id == p).select().first()
    email = auth.current_user.get('email')
    if row.user_email == email:
        form = Form(db.phone, csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            number = db(db.phone).select().last()
            number.update_record(contact_id=p)

            # We always want POST requests to be redirected as GETs.
            redirect(URL('edit_phones',p.id))
        return dict(form=form, row=row)

@action('delete_phone/<phone_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db,url_signer.verify())
def delete_phone(phone_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <contact_id> argument of the @action."""
    # We read the product.
    p = db.phone[phone_id]
    contact = p.contact_id
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('edit_phones',contact))
    if p is not None:
        db(db.phone.id == p).delete()
        redirect(URL('edit_phones',contact))

@action('edit_phone/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', session, db)
def edit_phone(contact_id = None,phone_id = None):
    p = db.contact[contact_id]
    row = db(db.contact.id == p).select().first()
    email = auth.current_user.get('email')
    c = db.phone[phone_id]
    print(c.contact_id)
    print(p.id)
    if p.id != c.contact_id:
        redirect(URL('index'))
    if p.id == c.contact_id:
        if row.user_email == email:
            form = Form(db.phone, csrf_session=session, formstyle=FormStyleBulma, record=c,deletable=False)
            if form.accepted:
                redirect(URL('edit_phones',p.id))
            return dict(form=form,row=row)
        else:
            redirect(URL('edit_phones',p.id))