# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Account, Category, Balance
from werkzeug.urls import url_parse
from sqlalchemy import func

@app.route('/')
@app.route('/index')
@login_required
def index():
    # user = {'username': 'Noah'}
    return render_template('index.html', title='Home')

@app.route('/data')
@login_required
def data():
    categories = Category.query.all()
    balance = Balance.query.all()
    account = Account.query.all()
    years = get_years()
    return render_template('data.html', title='Data', categories=categories, balance=balance, account=account, years=years)
def get_years():
    years = db.session.query(func.extract('year', Balance.date)).distinct().all()
    return [year[0] for year in years] 



@app.route('/login', methods=['GET', 'POST'])
def login():
    print("debug")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        # page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    # next_url = url_for('user', username=user.username, page=posts.next_num) \
        # if posts.has_next else None
    #    if posts.has_prev else None
    # form = EmptyForm()
    # return render_template('user.html', user=user, posts=posts.items,
    # next_url=next_url, prev_url=prev_url, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))