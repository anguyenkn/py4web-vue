"""
This file defines the database models
"""
from datetime import datetime

from . common import db, Field, auth
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

db.define_table('notes',
                Field('title', default="New Note"),
                Field('content', default=""),
                Field('color', 'integer', default=0), # colors have range 1 - 4
                Field('is_list', 'boolean', default=False),
                Field('has_star', 'boolean', default=False),
                Field('author', 'reference auth_user', default=get_user),
                Field('last_modified', 'date', 
                      default=datetime.now, update=datetime.now)                   # updates every time note updated
                )

db.commit()
