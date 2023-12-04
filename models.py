from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    token = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replies = db.relationship('Post', backref=db.backref('parent_post', remote_side=[id]))
    likes = db.relationship('Like', backref='post', lazy='joined')
    user = db.relationship('User', backref='posts')

class Like(db.Model):
    id = db.Column(db.String, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='likes')    

# add test users and posts
with app.app_context():
    db.create_all()
    db.session.add(User(id=1,username='admin',token='helloworld',is_admin=True))
    db.session.add(User(id=2,username='Bruker 1', token='1111111111'))
    db.session.add(Post(id=1,body='Innlegg nummer en',user_id=1))
    db.session.add(Post(id=2,body='Innlegg nummer to',user_id=2))
    db.session.add(Post(id=3,body='Reply under inlegg en',user_id=2,parent_post_id=1))
    db.session.add(Post(id=4,body='Reply på reply',user_id=1,parent_post_id=3))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
