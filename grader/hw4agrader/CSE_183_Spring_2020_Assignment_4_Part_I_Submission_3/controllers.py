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
@action('index', method='GET')
@action.uses('index.html', auth.user,db)
def index():
    user = auth.current_user
    rows=db(db.contact.user_email==auth.current_user.get('email')).select()
    return dict(user=user,rows=rows,url_signer=url_signer)

# The auth.user below forces login.
@action('add_contact',method=['GET', 'POST'])
@action.uses('contact_form.html',session,db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

# The auth.user below forces login.
@action('add_contact',method=['GET', 'POST'])
@action.uses('contact_form.html',session,db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db)
def edit_contact(contact_id=None):
    """Note that in the above declaration, the contact_id argument must match
    the <contact_id> argument of the @action."""
    # We read the contact.
    c = db.contact[contact_id]
    if c is None or c.user_email!=auth.current_user.get('email'):
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    form = Form(db.contact, record=c, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('delete_contact/<contact_id>', method=['GET', 'POST'])
@action.uses(session, db, url_signer.verify())
def delete_contact(contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    c = db.contact[contact_id]
    if c is None or c.user_email!=auth.current_user.get('email'):
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    db(db.contact.id==contact_id).delete()
    redirect(URL('index'))
