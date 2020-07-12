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
    return auth.current_user.get('email')

db.define_table(
    'person',
    Field('user_email', default=get_user_email),
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('phone_numbers')
)

db.person.id.readable = False
db.person.user_email.readable = False
db.person.phone_numbers.readable = False


db.define_table(
    'phone',
    Field('user_email', default=get_user_email),
    Field('person_id', db.person),
    Field('phone', requires=IS_NOT_EMPTY()),
    Field('kind', requires=IS_NOT_EMPTY())
)

db.phone.id.readable = False
db.phone.user_email.readable = False
db.phone.person_id.readable = False

db.commit()
