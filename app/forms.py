# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateTimeField, DateField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Email, Length
from app.models import User


class LoginForm(Form):
    email = StringField('email', validators=[Email()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False

        return True

##################
class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])


class PageDownForm(Form):
    title = StringField('title', validators=[DataRequired()])
    pagedown = PageDownField('Enter your markdown')

#####################


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class QuizForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])


class CardForm(Form):
    answer = TextAreaField('answer', validators=[DataRequired()])


class CompileForm(Form):
    code = TextAreaField('code', validators=[DataRequired()])


class WcForm(Form):
    picture = FileField('upload_pc', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'pictures only'),
        FileRequired('no picture upload')
    ])
    time1 = DateField('dt1')
    time2 = DateField('dt2')


class Contest(Form):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])
    st = DateTimeField('st', validators=[DataRequired()])
    choices1 = [('1', '30'), ('2', '60')]
    lt = SelectField('lt', choices=choices1)
    choices2 = [('1', '2'), ('2', '3')]
    mp = SelectField('mp', choices=choices2)
