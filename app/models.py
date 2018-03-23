# -*- coding: utf-8 -*-
from app import db, app
from hashlib import md5
from jieba.analyse.analyzer import ChineseAnalyzer
import flask_whooshalchemyplus as whooshalchemy

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

AttendGame = db.Table('AttendGame',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
    db.Column('code_content', db.String(1000))
)

Judge = db.Table('Judge',
    db.Column('judged_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
    db.Column('judger_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('comment', db.String(1000))
)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_title = db.Column(db.String(140))
    problem_description = db.Column(db.String(1400))

    timestamp = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    long_time = db.Column(db.Integer)

    attend_person = db.Column(db.Integer)
    max_person = db.Column(db.Integer)

    attenders = db.relationship('User', secondary=AttendGame,
                                backref=db.backref('games', lazy='dynamic'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120), index=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    cards = db.relationship('Card', backref='participant')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    is_authenticated = True
    is_active = True
    is_anonymous = False

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def get_id(self):
        return str(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode('utf8')).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    __searchable__ = ['body', 'title']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


class Question(db.Model):
    __searchable__ = ['title']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String(100))

    cards = db.relationship('Card', backref='discussion')

    def __repr__(self):
        return '<Question %r>' % (self.title)


whooshalchemy.whoosh_index(app, Post)
whooshalchemy.whoosh_index(app, Question)



class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return '<Card %r>' % (self.body)







