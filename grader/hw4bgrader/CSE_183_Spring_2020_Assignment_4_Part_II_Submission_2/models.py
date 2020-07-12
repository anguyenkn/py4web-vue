"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

# Define your table below
#
# db.define_table('thing', Field('name'))
#
# always commit your models to avoid problems later
#
# db.commit()
#


def get_user_email():
    return auth.current_user.get('email')

# contact table
db.define_table('contact',
                    Field('first_name'),
                    Field('last_name'),
                    Field('user_email', default=get_user_email)
)

# phone table, relates to contact table
db.define_table('phone',
                    Field('number'),
                    Field('kind'),
                    Field('contact_id', 'reference contact')
)

# We do not want these fields to appear in forms by default.
db.phone.contact_id.readable = False
db.phone.id.readable = False
db.phone.migrate = False

db.contact.id.readable = False
db.contact.user_email.readable = False
db.contact.migrate = False

db.commit()

