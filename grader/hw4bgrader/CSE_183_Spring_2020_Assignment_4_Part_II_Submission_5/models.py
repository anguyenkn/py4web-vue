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
    'contact',
     Field('first_name'),
     Field('last_name'),
     Field('user_email',default=get_user_email)
     )
db.contact.id.readable = False
db.contact.user_email.readable = False

db.define_table(
     'phone',
     Field('contact_id', 'reference contact'),
     Field('phone'),
     Field('type')
)

db.phone.id.readable = False
db.phone.contact_id.readable = False
db.phone.contact_id.ondelete = 'CASCADE'

db.commit()
