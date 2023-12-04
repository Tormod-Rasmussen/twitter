from flask import request, jsonify
from sqlalchemy.orm import joinedload ,subqueryload
import base64
import secrets
import string
from models import User, Post, Like, db
from functools import cache

@cache
def decode_token(encoded_token):
    token = encoded_token.split()[1]
    return base64.b64decode(token.encode()).decode()

def get_user_by_token(token):
    decoded_token = decode_token(token)
    return User.query.filter_by(token=decoded_token).first()

def validate_token(func):
    def wrapper(*args, **kwargs):
        user_token = request.headers.get('Authorization')
        try:
            user = get_user_by_token(user_token)
        except:
            return jsonify({'message': 'Invalid user token'}), 401
        return func(user, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def generate_new_token():
    availible_characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(availible_characters) for i in range(10))
    token_exists = User.query.filter_by(token=token).first()
    return token if not token_exists else generate_new_token()

def add_user(name,token):
    new_user = User(username=name, token=token)
    db.session.add(new_user)
    db.session.commit()

def encode_token(token):
    token = base64.b64encode(token.encode()).decode()
    return f'Basic {token}'

def create_user(username):
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        return {'error': 'User with this username already exists!'}, 400
    token = generate_new_token()
    add_user(username,token)
    encoded_token = encode_token(token)
    return {'message': 'User created successfully!',
            'username': username,
            'token': encoded_token}

def format_response(post, show_replies=False):
    post_dict = {
        'post_id': post.id,
        'post_body': post.body,
        'author': post.user.username,
        'author_id': post.user.id,
        'like_count': len(list(post.likes)),
        'reply_count': len(post.replies),
    }
    if show_replies:
        replies = [format_response(reply) for reply in post.replies]
        post_dict['replies'] = replies
    return post_dict

def post_exists(id):
    return Post.query.filter_by(id=id).first() is not None

def get_post_body(request):
    try:
        return request.json.get('body')
    except:
        return False

def add_post(post):
    db.session.add(post)
    db.session.commit()

def create_post(user, body):
    return Post(body=body, user_id=user.id)

def create_reply(user, body, parent):
    return Post(body=body, user_id=user.id, parent_post_id=parent)

def user_has_liked_post(user, post, session):
    return session.query(Like).filter_by(user_id=user.id, post_id=post.id).first() is not None

def like_post(user, post, session):
    like = Like(user_id=user.id, post_id=post.id)
    session.add(like)
    session.commit()

def unlike_post(user, post, session):
    like = session.query(Like).filter_by(user_id=user.id, post_id=post.id).first()
    session.delete(like)
    session.commit()
    session.refresh(user)
    session.refresh(post)

def get_replies(post):
    return [format_response(reply) for reply in post.replies]

def get_all_posts():
    query = Post.query.options(joinedload('user'), subqueryload('likes'))
    return query.filter_by(parent_post_id=None).all()

def find_post_by_id(post_id):
    query = Post.query.options(joinedload('user'), subqueryload('likes'))
    return query.get(post_id)

def is_admin_or_post_owner(user, post):
    return user.is_admin or user.id == post.user_id

def delete_post(post):
    db.session.delete(post)
    db.session.commit()

def edit_post(post, new_body):
    post.body = new_body
    db.session.commit()

def get_like_list(post_id):
    post = find_post_by_id(post_id)
    return {'liked_users': [like.user.username for like in post.likes]}