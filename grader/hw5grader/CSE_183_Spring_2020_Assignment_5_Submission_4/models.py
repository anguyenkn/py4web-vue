"""
This file defines the database models
"""
import datetime

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

def get_time():
    return datetime.datetime.utcnow()

# Use these tables.

db.define_table('post',
                Field('user_email', default=get_user_email),
                Field('post_text', 'text'),
                Field('ts', 'datetime', default=get_time),
                )

db.define_table('thumb',
                Field('user_email', default=get_user_email()),
                Field('post_id', 'reference post'),
                Field('rating', 'integer', default=0)
                )

db.commit()
