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

from py4web import action, request, redirect, URL
from py4web.utils.url_signer import URLSigner

from . common import session

# We build a URL signer.
url_signer = URLSigner(session)

@action('index', method='GET')
@action.uses('index.html', session)
def index():
    state1 = session.get('1', 'Undefined')
    state2 = session.get('2', 'Undefined')
    counter1 = session.get('counter1', 7)
    counter2 = session.get('counter2', 3)
    # We pass the URL signer to the template, so we can sign URLs there.
    return dict(state1=state1, state2=state2, counter1=counter1, counter2=counter2, url_signer=url_signer)


@action('toggle/<id>')
@action.uses(session, url_signer.verify())
def toggle(id=None):
    # Note that id is an int, due to the type declaration.
    if id is not None:
        # In a session, all keys need to be strings.
        session[id] = request.params.get('thumb').upper()
    redirect(URL('index'))


@action('count/<name>')
@action.uses(session, url_signer.verify())
def count(name=None):
    if name is not None:
        arrow = request.params.get('arrow')
        if not name in session.keys():
            session[name] = 0
        if(arrow == 'reset'):
            session[name] = 0
        elif(arrow == 'up'):
            session[name] += 1
        else:
            session[name] -= 2
    redirect(URL('index'))