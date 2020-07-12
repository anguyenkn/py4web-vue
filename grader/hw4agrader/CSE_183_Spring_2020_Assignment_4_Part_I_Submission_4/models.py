"""
This file defines the database models
"""
import datetime

from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email')


db.define_table('contacts',
                Field('first_name'),
                Field('last_name'),
                Field('user_email', default=get_user_email)
                )

# We do not want these fields to appear in forms by default.
db.contacts.id.readable = False
db.contacts.user_email.readable = False
# add first and last name as readable


db.commit()
