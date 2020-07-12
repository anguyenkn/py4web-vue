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

# Let us import some convenience functions.
from .models import get_user

# Let us import the starrater component code.
from .components.notes import Notes


class ImageRater(Notes):

    def get_rating(self, id=None):
        """Gets the rating for a given id. """
        if id is None:
            return dict(rating=0)
        s = db((db.rating.image == int(id)) &
               (db.rating.rater == get_user())).select().first()
        return dict(rating=None if s is None else s.rating)

    def set_rating(self, id=None):
        """Sets the rating."""
        print("id is " + str(id))
        assert id is not None
        db.rating.update_or_insert(
            ((db.rating.image == int(id)) & (db.rating.rater == get_user())),
            image = int(id),
            rater = get_user(),
            rating=int(request.params.rating),
        )
        return "ok"


image_rater = ImageRater('rate', session, db=db)

IMAGES = ["rubber-duck.jpg", "rabbit.jpg", "teddy_bear.jpg",
    "colander.jpg", "coffeecup.jpg", "cowboy_hat.jpg"]

url_signer = URLSigner(session)


# The auth.user below forces login.
@action('index')
@action.uses('index.html', db, url_signer)
def index():
    # notes = db(db.notes).select().as_list()
    # for img in images:
    #     img['rater'] = image_rater(id=img['id'])
    x = []
    return dict(
        get_notes_url = URL('get_notes', signer=url_signer)
    )

@action('get_notes')
@action.uses(db, auth.user, session, url_signer.verify())
def get_notes():
    notes = db(db.notes).select().as_list()
    # for img in images:
    #     img['rater'] = image_rater(id=img['id'])
    print(notes)
    return dict(notes=notes)

