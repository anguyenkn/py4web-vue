"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

def get_user_email():
     return auth.current_user.get('email')

### Define your table below

db.define_table(
  'contact',
  Field('user_email', default=get_user_email),
  Field('first_name', requires=IS_NOT_EMPTY()),
  Field('last_name', requires=IS_NOT_EMPTY())
)

db.contact.id.readable = False
db.contact.user_email.readable = False


db.define_table(
  'phones',
  Field('phone', requires=IS_NOT_EMPTY()),
  Field('kind', requires=IS_NOT_EMPTY()),
  Field('contact_id', 'reference contact')
)

db.phones.id.readable = False
db.phones.contact_id.readable = False

db.commit()
