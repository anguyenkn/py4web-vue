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

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . models import get_user_email

url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        add_posts_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_peopleLIKE_url = URL('get_peopleLIKE', signer=url_signer),
        get_peopleDISLIKE_url = URL('get_peopleDISLIKE', signer=url_signer),

        # Add other callbacks here.
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user)
def get_posts():
    # Complete.
    posts = db(db.post).select(orderby=~db.post.ts).as_list() # Just to keep code from breaking.
    for p in posts:
        r = db(db.auth_user.email == p["user_email"]).select().first()
        name = r.first_name + " " + r.last_name if r is not None else "Unknown"
        p["usernames"] = name
    return dict(posts=posts)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user)
def add_post():
    # Complete.
    id = db.post.insert(
        post_text = request.json.get('post_text'),
    )
    return dict(id=id) # You need to fill this in.
    
@action('get_rating')
@action.uses(url_signer.verify(), auth.user, db)
def get_rating():
    postID = request.params.get('postID')
    #print ("This is the postID = ", end = ''), print(postID)
    #user_id = auth.current_user.get('id')
    user_email = get_user_email(),
    if postID is not None:
        rating_entry = db((db.thumb.post_id == postID) & (db.thumb.user_email == user_email)).select().first()
        rating = rating_entry.rating if rating_entry is not None else 0
        #print ("This is the rating = ", end = ''), print(rating)
    return dict(rating=rating)

@action('set_rating', method='POST')
@action.uses(url_signer.verify(), auth.user, db)
def set_rating():
    postID = request.json.get('postID')

    user_id = auth.current_user.get('id')
    rating = request.json.get('rating')

    user_emailREAL = get_user_email(),
    
    if postID is not None:
        db.thumb.update_or_insert(
            ((db.thumb.post_id == postID) & (db.thumb.user_email == user_emailREAL)),
            post_id=postID,
            user_email = user_emailREAL,
            rating=rating, 
        )
    #selector = db(db.thumb).select((db.thumb.post_id == postID) & (db.thumb.user_email == user_emailREAL))
    #print(selector.post_id)
    #print(selector.user_email)
    #print(selector.rating)
    return "ok"
    
@action('get_peopleLIKE')
@action.uses(url_signer.verify(), auth.user, db)
def get_peopleLIKE():
    postID = request.params.get('postID')    
    user_email = get_user_email(),
    if postID is not None:
        #I think we need to find the thumb reference instead.
        #There is going to be multiple people who liked it not just one. 
        #Maybe a for loop that sets a string of likes, and makes that the first element in a list
        #And then another string of dislikes, second element in a list. 
        rating_entry = db(db.thumb.post_id == postID).select().as_list()
        LIKERS = "Liked by "
        DISLIKERS = ""
        for p in rating_entry:
            #X is the user_email, but I had to trim the parantheses and commas 
            x = p["user_email"]
            x = x[2:]
            x = x[:-3]

            r = db(db.auth_user.email == x).select().first()
            name = r.first_name + " " + r.last_name if r is not None else "Unknown"

            if p["rating"] == 1:
                LIKERS = LIKERS + name + ", "

            DISLIKERS = "There"
            print(p["rating"])
            
        if LIKERS == "Liked by ":
            LIKERS = ""
        else:
            LIKERS = LIKERS[:-2]
        epicList = [LIKERS, DISLIKERS]

    return dict(epicList=epicList)
    
    
    
    
@action('get_peopleDISLIKE')
@action.uses(url_signer.verify(), auth.user, db)
def get_peopleDISLIKE():
    postID = request.params.get('postID')    
    user_email = get_user_email(),
    if postID is not None:
        #I think we need to find the thumb reference instead.
        #There is going to be multiple people who liked it not just one. 
        #Maybe a for loop that sets a string of likes, and makes that the first element in a list
        #And then another string of dislikes, second element in a list. 
        rating_entry = db(db.thumb.post_id == postID).select().as_list()
        DISLIKERS = "Disliked by "
        for p in rating_entry:
            #X is the user_email, but I had to trim the parantheses and commas 
            x = p["user_email"]
            x = x[2:]
            x = x[:-3]

            r = db(db.auth_user.email == x).select().first()
            name = r.first_name + " " + r.last_name if r is not None else "Unknown"

            if p["rating"] == 2:
                DISLIKERS = DISLIKERS + name + ", "


        if DISLIKERS == "Disliked by ":
            DISLIKERS = ""
        else:
            DISLIKERS = DISLIKERS[:-2]
        epicList = [DISLIKERS]
    return dict(epicList=epicList)
    
    
#What if we make something that calls add_post() and then redirects to get_posts()?
    
@action('delete_post', method="POST")
@action.uses(url_signer.verify(), auth.user)
def delete_post():
    id = request.json.get('id')
    if id is not None:
        db(db.post.id == id).delete()
    return("ok")
    
# Complete.