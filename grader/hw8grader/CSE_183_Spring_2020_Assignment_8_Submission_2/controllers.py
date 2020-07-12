"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""


import uuid

from py4web import action, request, abort, redirect, URL, Field, HTTP
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
import os.path
import tempfile
import uuid

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url

# Let us import some convenience functions.
from .models import get_user,get_user_email
import datetime

# Let us import the starrater component code.
#from .components.thumbrater import ThumbRater

url_signer = URLSigner(session)


def get_name_from_email(e):
    """Given the email of a user, returns the name."""
    u = db(db.auth_user.email == e).select().first()
    return "" if u is None else u.first_name + " " + u.last_name



     
# The auth.user below forces login.
@action('index')
#@action.uses('index.html', url_signer)
@action.uses(auth.user, url_signer, session, db, 'index.html')  
def index():
    # This is used just to ensure the db is initialized.
    '''
    if db(db.images).count() == 0:
        setup()
    # Returns to the templage the list of images.
    images = db(db.images).select().as_list()
    # I add a star rater to each image, so each image can be rated.
    for img in images:
        img['rater'] = image_rater(id=img['id'])
        
    '''    
    
    #print("IN index")
    
    posts = []    
    #posts = TEST_POSTS
        
    return dict(posts=posts,
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        posts_url = URL('posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        update_post_url  = URL('update_post', signer=url_signer),
        set_star_url = URL('set_star', signer=url_signer),
        set_color_url = URL('set_color', signer=url_signer),       
        image_url = URL('image_post', signer=url_signer),
        delete_url = URL('delete_post', signer=url_signer),
        user_email = auth.current_user.get('email'),
        author_name = auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')    
        )




     
    
@action('add_post', method="POST")
# Notice that if you omit 'db' below, no changes are saved.
@action.uses(auth.user, url_signer, session, db, url_signer.verify())  
#@action.uses(url_signer.verify(), db)
def add_post():
    # NOTE: axios sends requests in json, so their content
    # is available in request.json.
    #print("Neel py in add_post id")
    
    
    content = request.json.get('content')
    title = request.json.get('title')
    background_color = request.json.get('background_color')
    rating = request.json.get('rating')
    
    
#########################################   
    #with open(filename, 'rb') as stream: 
    db.post.insert(email=get_user_email(), content = content, title = title, background_color = background_color, rating = rating, post_date = datetime.datetime.utcnow())
#########################################    
    
    
    
    '''        
    db.post.insert(email=get_user_email(), content = content, title = title, background_color = background_color, rating = rating, post_date = datetime.datetime.utcnow())
    '''

    db.commit()
            
    return dict()

@action('posts', method="GET")
@action.uses(db, auth.user, session, url_signer.verify())
#@action.uses(db, session, url_signer.verify())
def get_posts():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    #return dict(posts=TEST_POSTS)
    '''
db.define_table("post",
                Field('email', default=get_user_email),
                Field('content', 'text'),
                Field('title', 'text'),
                Field('background_color', 'text', default=get_bk_color),
                Field('rating', 'integer', default=0),
                Field('post_date', 'datetime', default=get_time),
                )
    '''                    

    
    
    #posts = db(db.post).select().as_list()
    #print("IN get_posts")
    

    
    posts = []
    posts = get_post_listing()
    #print(posts)
        
    return dict(posts=posts)
    
    
def get_post_listing():

    posts = db(db.post.email == auth.current_user.get("email")).select(orderby=~db.post.rating|~db.post.post_date).as_list()
    #posts = db(db.post).select(orderby=~db.post.rating|~db.post.post_date).as_list()
    
    return posts;
'''   
    posts_listing = []   
    posts = db(db.post).select(orderby=~db.post.rating).as_list()
    
    for one_post in posts:
        main_post_id = one_post['id']
        post_replys = db(db.post.is_reply == main_post_id).select(orderby=~db.post.id).as_list()
        for one_reply in post_replys:
            one_reply['author'] = get_name_from_email(one_reply['email'])
            posts_listing.append(one_reply)
            
    #print(posts_listing)

    return posts_listing;        
'''

    

@action('update_post', method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
#@action.uses(db, session, url_signer.verify())
def update_save_post():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    #return dict(posts=TEST_POSTS)

    #print("NEELLLLLLLLLLLLLLLLL Neel py update_save_post():");  
    
    
    
    post_id = request.json.get('post_id')
    content = request.json.get('content')
    title = request.json.get('title')
    #background_color = request.json.get('background_color')
    #rating = request.json.get('rating')
    
    if(CheckUserIdMatchesAuthUser(post_id) == False):
        return dict()    
    
    #print(post_id,content,title)
            
    #db.post.insert(email=get_user_email(), content = content, title = title, background_color = background_color, rating = rating, post_date = datetime.datetime.utcnow())
    #db((auth_email == db.thumb.user_email) & (db.thumb.post_id == post_id)).update(post_id = post_id, rating=new_rating)
    
    #db(db.post.id == post_id).update(content = content, title = title, background_color = background_color, 
    #                                    rating = rating, post_date = datetime.datetime.utcnow())

    db(db.post.id == post_id).update(content = content, title = title, post_date = datetime.datetime.utcnow())


    
    db.commit()
    
    return dict()






    
    
@action('set_star', method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
##@action.uses(db, session, url_signer.verify())
def set_star():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    #return dict(posts=TEST_POSTS)

    #print("set_star():");  
    
   
    
    post_id = request.json.get('post_id')
    rating = request.json.get('rating')
    
    #print(post_id,rating)
    
    if(CheckUserIdMatchesAuthUser(post_id) == False):
        return dict()     
            
    #db.post.insert(email=get_user_email(), content = content, title = title, background_color = background_color, rating = rating, post_date = datetime.datetime.utcnow())
    #db((auth_email == db.thumb.user_email) & (db.thumb.post_id == post_id)).update(post_id = post_id, rating=new_rating)
    db(db.post.id == post_id).update(rating = rating, post_date = datetime.datetime.utcnow())
    
    db.commit()
    return dict()
    

@action('set_color', method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
#@action.uses(db, session, url_signer.verify())
def set_color():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    #return dict(posts=TEST_POSTS)

    #print("set_color():");  

   
    
    post_id = request.json.get('post_id')
    background_color = request.json.get('background_color')
    
    #print(post_id,background_color)
    
    if(CheckUserIdMatchesAuthUser(post_id) == False):
        return dict()     
            
    #db.post.insert(email=get_user_email(), content = content, title = title, background_color = background_color, rating = rating, post_date = datetime.datetime.utcnow())
    #db((auth_email == db.thumb.user_email) & (db.thumb.post_id == post_id)).update(post_id = post_id, rating=new_rating)
    db(db.post.id == post_id).update(background_color = background_color, post_date = datetime.datetime.utcnow())
    
    db.commit()
    return dict()



@action('image_post', method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
#@action.uses(db, session, url_signer.verify())
def image_post():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    #return dict(posts=TEST_POSTS)

    #print("image_post():");  
    
    post_id = request.forms.get('post_id')
    #print(post_id)
            
    f = request.files.get('file')
    if f is None:
        print("No file")
    else:
        print("Received file:", f.filename)

        #print("Content:", f.file.read())
        

    if(CheckUserIdMatchesAuthUser(post_id) == False):
        return dict() 

    '''            
    #name, ext = os.path.splitext(f.filename)
    #if ext not in ('.png', '.jpg', '.jpeg'):
    #   return "File extension not allowed."

    save_path = "/tmp/HW8"
    if not os.path.exists(save_path):
         os.makedirs(save_path)

    
    file_path = "{path}/{file}".format(path=save_path, file=f.filename)
    print(os.path.realpath(file_path))      
    f.save(file_path)
    tempfile
      '''

    file_path = ""

    try:
    
        save_path = "/tmp/HW8" + str(uuid.uuid4())
        if not os.path.exists(save_path):
             os.makedirs(save_path)

        file_path = "{path}/{file}".format(path=save_path, file=f.filename)
        #print(os.path.realpath(file_path))      
        f.save(file_path)
        #print("Saved OK")
    finally:
         stringT = ""
    
    db(db.post.id == post_id).update(image_filename = os.path.realpath(file_path), post_date = datetime.datetime.utcnow())
    
    return "File successfully saved to '{0}'.".format(save_path)

    
@action('delete_post', method="POST")
# Notice that if you omit 'db' below, no changes are saved.
@action.uses(db, auth.user, session, url_signer.verify())
#@action.uses(url_signer.verify(), db)
def delete_post():
    # NOTE: axios sends requests in json, so their content
    # is available in request.json.

    post_id = request.json.get('post_id')
    
    #print("Need in delete post py value", post_id)    
    
    
    if(CheckUserIdMatchesAuthUser(post_id) == False):
        return dict()
        
    
    #print("Need in delete post py value", post_delete_id);
    
    del db.post[post_id]
    
    db.commit()
     
    # We return the id to the web interface, so it can keep track of it.
    return dict()

@action.uses(auth.user)
def CheckUserIdMatchesAuthUser(post_id):
    ret = True
    p = db.post[post_id]
    if p is None:
        ret = False
    elif p.email != auth.current_user.get('email'):
        ret = False
    return