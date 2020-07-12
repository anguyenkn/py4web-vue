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

@action('index', method='GET')
@action.uses('index.html', db, session)
def view_products():

    sortStatus = request.params.get('sort')  # stores what is returned from the paramaters
    rows = db(db.product).select()           # queries an the unsorted table
    state = None                             # set state

    if sortStatus == "asc":
        rows = db().select( orderby=db.product.product_cost) # queries by product_cost in ascending order
        state = 1                                            # set state to show asc up arrow
    elif sortStatus == 'desc':
        rows = db().select(orderby=~db.product.product_cost) # queries by product_cost in ascending order in reverse
        state = 2                                            # set state to show desc down arrow

    return dict(state=state, rows=rows, signed_url=signed_url)


@action('add_product', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def add_product():
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form )

@action('edit_product/<product_id>', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def edit_product(product_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    print("inside edit_product" )
    p = db.product[product_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)


@action('delete_product/<product_id>', method=['GET', 'POST'])
@action.uses(db, signed_url.verify(), session)
def delete_product(product_id=None):

    p = db.product[product_id]
    if p is not None:
        print("The product deleted is ", p)
        del db.product[product_id]

    redirect(URL('index'))
