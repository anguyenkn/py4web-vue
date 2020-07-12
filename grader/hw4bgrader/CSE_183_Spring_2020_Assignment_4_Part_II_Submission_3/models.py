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

def get_time():
    return datetime.datetime.utcnow()

def get_user_email():
    return auth.current_user.get('email')

def get_user_id():
    return auth.current_user.get('id')


db.define_table(
    'contact',
    Field('first_name', required=False),
    Field('last_name', required=False),
    Field('user_email', default=get_user_email)
)

db.define_table(
    'phone',
    Field('number'),
    Field('kind'),
    Field('phone_user')
)

db.contact.first_name.requires = IS_NOT_EMPTY()
db.contact.last_name.requires = IS_NOT_EMPTY()

db.phone.number.requires = IS_NOT_EMPTY()
db.phone.kind.requires = IS_NOT_EMPTY()

db.contact.id.readable = False
db.contact.user_email.readable = False

db.phone.id.readable = False
db.phone.phone_user.readable = False



db.commit()
