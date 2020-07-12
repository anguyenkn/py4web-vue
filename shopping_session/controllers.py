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

# Let's import the product definitions.
# In real life, you would have a db table, but for simplicity
# here it is a static list.
from . products import PRODUCT_LIST, split_list, product_dict

# -----------------------------

# Builds a URL signer.
url_signer = URLSigner(session=session)

@action('index', method='GET')
@action.uses('index.html', session)
def index():
    # You need to add here the code to display the shopping cart.
    # Can you get the shopping cart to also display a max of 3 items per row?
    cart = session.get('cart', [])
    return dict(products=split_list(PRODUCT_LIST, 3),
                cart=split_list(cart, 3),                 
                product_dict=product_dict,
                url_signer=url_signer)


# This controller is severely incomplete.  You need to add the handling
# of the parameters, the URL
# signature verification, and all its functionality.
@action('buy/<id>')
@action.uses(session, url_signer.verify())
def buy(id=None):
    if not 'cart' in session.keys():
        session['cart'] = []
    if id is not None:
        session['cart'] += [PRODUCT_LIST[int(id)-1]]
    redirect(URL('index'))

@action('remove/<idx:int>')
@action.uses(session, url_signer.verify())
def buy(idx=None): 
    if idx is not None:
        temp = session['cart']
        temp.pop(idx) 
        session['cart'] = temp 
    redirect(URL('index')) 