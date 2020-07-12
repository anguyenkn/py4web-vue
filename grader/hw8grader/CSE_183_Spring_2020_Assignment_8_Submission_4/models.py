"""
This file defines the database models
"""
import time

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
    return time.time_ns()//10**6 #to match js Date.now()

db.define_table('notes',
                Field('email', default=get_user_email),
                Field('title', 'text', default=' '),
                Field('content', 'text', default=' '),
                Field('note_date', default=get_time),
                Field('color', 'text', default='is-white'),
                Field('pinned', 'integer', default=0)
                )
db.commit()