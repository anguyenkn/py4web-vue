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

def get_email():
    return auth.current_user.get("email")

db.define_table(
    'user', 
    Field('first_name'), 
    Field('last_name'), 
    Field('user_email', default=get_email)
    
)

db.define_table(
    'contacts',
    Field('first_name', required=True),
    Field('last_name', required=True), 
    Field('creator_email', default=get_email)
)

db.contacts.creator_email.readable=False

db.define_table(
    'phones', 
    Field('number', required=True), 
    Field('phone_name', required=True), 
    Field('contact_id'),
    Field('creator_email', default=get_email)
)

db.phones.creator_email.readable=False
db.phones.contact_id.readable=False

db.commit()








