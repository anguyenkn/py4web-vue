"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_name():
    if auth.current_user:
        return auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')
    else:
        return None

def get_time():
    return datetime.datetime.utcnow()

db.define_table('notes',
                Field('email', default=get_user_email),
                Field('author', default=get_user_name),
                Field('title', 'string'),
                Field('content'),
                Field('color', 'string', default="white"),
                Field('star', 'integer', default=0),
                Field('is_archived', 'integer', default=0),
                Field('last_modified', 'datetime', default=get_time),
                Field('image_url', 'string', default=None),
                Field('shared_email', 'string', default=""),
                )

db.commit()
