from flask import *
from flask_login import login_user, logout_user, current_user, login_required
from .forms import *
from app import app, db, lm, oid
from .models import User, Post, Question, Card
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from .run_code import *

@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title = 'Home',
        form = form,
        posts = posts)


def aft_login(e, p):
    user = User.query.filter_by(email=e).first()
    if user is None:
        nickname = e.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(email=e, password=p, nickname=nickname)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    print(g.search_form)
    #g.search_form = SearchForm()
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    #post
    if form.validate():
        flash('Login requested for email=' + form.email.data)
        """return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        OpenID认证异步发生。如果认证成功的话，Flask - OpenID
        将会调用一个注册了oid.after_login装饰器的函数"""
        session['remember_me'] = form.remember_me.data
        aft_login(form.email.data, form.password.data)
        #return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))


@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    print(query)
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    titles = Question.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    print(titles)
    return render_template('search_results.html',
        query=query,
        results=results,
        titles=titles)


@app.route('/look')
@app.route('/look/<int:page>')
def look(page=1):
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('look.html',
                           posts=posts)


@app.route('/forum', methods=['POST', 'GET'])
@app.route('/forum/<int:page>', methods=['POST', 'GET'])
def forum(page=1):
    form = QuizForm()
    if form.validate():
        question = Question(title=form.title.data, timestamp=datetime.utcnow())
        db.session.add(question)
        db.session.commit()

        question = Question.query.order_by(Question.timestamp.desc()).first()
        card = Card(body=form.body.data, timestamp=datetime.utcnow(), participant=g.user, discussion=question)
        db.session.add(card)
        db.session.commit()
        flash('Your question is now live!')
        return redirect(url_for('forum'))
    questions = Question.query.order_by(Question.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('forum.html',
                           questions=questions,
                           form=form)


@app.route('/discuss/<pk>', methods=['POST', 'GET'])
@app.route('/discuss/<pk>/<int:page>', methods=['POST', 'GET'])
def discuss(pk, page=1):
    form = CardForm()
    if form.validate():
        card = Card(body=form.answer.data, timestamp=datetime.utcnow(), participant=g.user, question_id=pk)
        db.session.add(card)
        db.session.commit()
        flash('Your answer is now live!')
        return redirect(url_for('discuss', id=pk))

    cards = Card.query.filter_by(question_id=pk).order_by(Card.timestamp).paginate(page, POSTS_PER_PAGE, False)
    question = Question.query.filter_by(id=pk)
    title = question[0].title
    #print(cards[0].body)
    return render_template('card.html',
                           cs=cards,
                           form=form,
                           pk=pk,
                           title=title)


@app.route('/code', methods=['POST', 'GET'])
def code():
    form = CompileForm()
    d = dict()
    if form.validate():
        program = form.code.data
        print(program)
        d = runcode(program)
        print(d)
        return render_template('code.html',
                               form=form,
                               d=d)
    return render_template('code.html',
                           form=form,
                           d=d)