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

from py4web.utils.auth import Auth
auth = Auth(session, db)
auth.enable()

# The auth.user below forces login.
@action('index', method='GET')
@action.uses(auth.user, 'index.html', db, signed_url)
def index():
    rows = db(db.person.user_email == auth.current_user.get('email')).select()
    return dict(rows=rows, url_signer=url_signer)

@action('delete_contact/<person_id>', method=['GET', 'POST'])
@action.uses(auth.user, db, session, signed_url.verify())
def delete_contact(person_id=None):
    p = db.person[person_id]
    if p is None:
        redirect(URL('index'))
    else:
        db((db.person.id==person_id) & (p.user_email == auth.current_user.get('email'))).delete()
        redirect(URL('index'))

@action('add_contact', method=['GET', 'POST'])
@action.uses('add_contact.html', session, db)
def add_contact():
    form = Form(db.person, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<person_id>', method=['GET', 'POST'])
@action.uses('add_contact.html', auth.user, db, session, db)
def edit_contact(person_id=None):
    """Note that in the above declaration, the person_id argument must match
    the <person_id> argument of the @action."""
    # We read the person.
    p = db.person[person_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    if ((db.person.id==person_id) and (p.user_email == auth.current_user.get('email'))):
        form = Form(db.person, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            # We always want POST requests to be redirected as GETs.
            redirect(URL('index'))
    else:
        redirect(URL('index'))
    return dict(form=form)