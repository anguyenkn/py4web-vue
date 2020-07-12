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

from py4web import action, URL

@action("index")
@action.uses("index.html")
def index1():
    return dict()

@action("bullets")
@action.uses("bullets.html")
def index2():
    return dict()

@action("columns")
@action.uses("columns.html")
def index3():
    return dict()

@action("images")
@action.uses("images.html")
def index4():
    return dict()

@action("many_columns")
@action.uses("many_columns.html")
def index5():
    return dict()

@action("tables")
@action.uses("tables.html")
def index6():
    return dict()

@action("icons")
@action.uses("icons.html")
def index7():
    return dict()

@action("tiles")
@action.uses("tiles.html")
def index8():
    return dict()

