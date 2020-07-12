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
@action.uses('index.html', url_signer)
def index():
    return dict(
        # This is the signed URL for the callback.
        load_rows_url = URL('load_rows', signer=url_signer),
        add_person_url = URL('add_person', signer=url_signer),
        delete_person_url = URL('delete_person', signer=url_signer),
    )

@action('load_rows')
# Note that we do not use a template.  This is a JSON API, not a "web page".
@action.uses(url_signer.verify())
def load_rows():
    rows = db(db.people).select().as_list()
    return dict(rows=rows)

@action('add_person', method="POST")
# Notice that if you omit 'db' below, no changes are saved.
@action.uses(url_signer.verify(), db)
def add_person():
    # NOTE: axios sends requests in json, so their content
    # is available in request.json.
    id = db.people.insert(
        first_name = request.json.get('first_name'),
        last_name = request.json.get('last_name')
    )
    # We return the id to the web interface, so it can keep track of it.
    return dict(id=id)

@action('delete_person', method="POST")
@action.uses(url_signer.verify(), db)
def delete_person():
    id = request.json.get('id')
    if id is not None:
        db(db.people.id == id).delete()
    return "ok" # Just to return something.
