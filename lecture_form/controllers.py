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

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url

# --------------------------------------
# Using the session to store information

@action('index', method='GET')
@action.uses('index.html')
def index():
    return dict()

@action('index', method='POST')
@action.uses(session) # Important!  Otherwise, the changes to session are not saved.
def post_index():
    # request is a Bottle object.
    # For its documentation, see https://bottlepy.org/docs/dev/tutorial.html#request-data
    # and https://bottlepy.org/docs/dev/tutorial.html#html-form-handling
    u = request.params.get('username')
    session['username'] = u
    print("You said you are:", u)
    # We always redirect when we get a POST.
    redirect(URL('confirmation'))


@action('confirmation', method='GET')
@action.uses(session, "confirmation.html")
def confirmation():
    for cookie_name in request.cookies.keys():
        cookies = request.cookies.getall(cookie_name)
        for cookie_value in cookies:
            print("Cookie name:", cookie_name, "Cookie value:", cookie_value)
    for k in session.keys():
        print(k, session.get(k))
    u = session.get('username') or 'Your username is not defined'
    return dict(username=u)


# ------------------------------------
# This page is accessible only to logged-in users.

@action('add_product', method=['GET', 'POST'])
@action.uses('product_form.html', session, db, auth.user)
def add_product():
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('add_product'))
    return dict(form=form)

@action('view_products', method='GET')
@action.uses('view_products.html', db)
def view_products():
    # We get all the table rows, via a query.
    rows = db(db.product).select()
    return dict(rows=rows)

@action('edit_product/<product_id>', method=['GET', 'POST'])
@action.uses('product_form.html', session, db, auth.user)
def edit_product(product_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.product[product_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('view_products'))
    form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('view_products'))
    return dict(form=form)

