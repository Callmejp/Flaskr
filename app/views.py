from flask import *
from flask_login import login_user, logout_user, current_user, login_required
from .forms import *
from app import app, db, lm, oid
from .models import User, Post, Question, Card, Game, AttendGame
from datetime import datetime, timedelta
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, languageId, basedir
from .run_code import pa_chong, make_wc
import markdown, time


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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))"""
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title='Home',
        posts=posts)


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


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    #print(query)
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    print(results)
    titles = Question.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    print(titles)
    return render_template('search_results.html',
        query=query,
        results=results,
        titles=titles)


@app.route('/look')
@app.route('/look/<int:page>')
@login_required
def look(page=1):
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('look.html',
                           posts=posts)


@app.route('/forum', methods=['POST', 'GET'])
@app.route('/forum/<int:page>', methods=['POST', 'GET'])
@login_required
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
@login_required
def discuss(pk, page=1):
    form = CardForm()
    if form.validate():
        card = Card(body=form.answer.data, timestamp=datetime.utcnow(), participant=g.user, question_id=pk)
        db.session.add(card)
        db.session.commit()
        flash('Your answer is now live!')
        return redirect(url_for('discuss', pk=pk))

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
@login_required
def code():
    """
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
                           d=d)"""
    if request.method == 'POST':
        data = json.loads(request.form.get('data'))
        content = data["code"]
        language = languageId[data["id"]]
        print(content)
        print(language)
        d = {
            'code': content,
            'language': language
        }
        dic = pa_chong(d)
        print(dic)
        return dic
    return render_template('code_temp.html')


@app.route('/write', methods=['POST', 'GET'])
@login_required
def write():
    form = PageDownForm()

    if request.method == 'POST':
        if form.title.data == "" or form.pagedown.data == "":
            flash("标题或文章内容不能为空")
            return render_template('write.html',
                                   form=form)
        post = Post(body=form.pagedown.data, title=form.title.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        print(form.title.data == "")
        flash('Your article is now live!')
        return redirect(url_for('index'))
    return render_template('write.html',
                           form=form)


@app.route('/article/<pk>', methods=['GET', 'POST'])
@login_required
def article(pk):
    a = Post.query.filter_by(id=pk)
    title = a[0].title
    body = a[0].body
    md = markdown.markdown(body)
    html = '{% extends "base.html" %}{% block content %}<h1>标题：' + title + '<br>内容如下：</h1><div>' + str(md) + '</div>{% endblock %}'
    html = html.encode('utf-8')
    print(html)
    with open('app/templates/article.html', 'wb') as f:
        f.write(html)
    return render_template('article.html')


@app.route('/wordcloud', methods=['GET', 'POST'])
@login_required
def wc():
    form = WcForm()
    if form.validate_on_submit():
        print("come in")
        pic = form.picture.data
        pic.save(basedir + "\\app\\static\\try.jpg")
        st_time = form.time1.data
        ed_time = form.time2.data
        data = Card.query.all()
        make_wc(st_time, ed_time, data)
        return redirect(url_for('show_wc'))
    return render_template('wc.html',
                           form=form)


@app.route('/show_wordcloud', methods=['POST', 'GET'])
@login_required
def show_wc():
    return render_template('show.html',
                           val1=time.time())


@app.route('/contest', methods=['POST', 'GET'])
@app.route('/contest/<int:page>')
@login_required
def contest(page=1):
    form = Contest()
    games = Game.query.order_by(Game.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    if form.validate_on_submit():
        print(form.data)
        lt = 60
        if form.lt.data == '1':
            lt = 30
        mp = 3
        if form.mp.data == '1':
            mp = 2

        end = form.st.data + timedelta(seconds=lt*60)
        game = Game(problem_title=form.title.data, problem_description=form.body.data, start_time=form.st.data,
                    end_time=end, long_time=lt, max_person=mp, timestamp=datetime.utcnow(), attend_person=1)
        #db.session.add(game)
        game.attenders.append(g.user)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('contest', form=form, games=games))
    return render_template('contest.html',
                           form=form,
                           games=games, datetime=datetime)


@app.route('/contest/<title>/<gid>', methods=['POST', 'GET'])
@login_required
def contest_detail(title, gid):

    if request.method == 'POST':
        data = json.loads(request.form.get('data'))
        content = data["code"]
        print(content)
        #attend = db.session.query(AttendGame).filter_by(game_id=gid, user_id=g.user.id)[0]
        db.session.insert(AttendGame).values()
        db.session.add(gg)
        db.session.commit()
        return ""
    c = Game.query.filter_by(id=gid)[0]
    users = c.attenders
    print(users)
    return render_template('contest_detail.html',
                           c=c, users=users, datetime=datetime, title=title, gid=gid)













