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

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None



                
                

def get_time():
    return datetime.datetime.utcnow()

def get_bk_color():
    return "has-background-primary"    

db.define_table("post",
                Field('email', default=get_user_email),
                Field('content', 'text'),
                Field('title', 'text'),
                Field('background_color', 'text', default=get_bk_color),
                Field('rating', 'integer', default=0),
                Field('post_date', 'datetime', default=get_time),
                Field('image_filename', 'text'),
                
                )

db.commit()
