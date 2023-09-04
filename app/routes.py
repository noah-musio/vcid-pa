# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import AccountForm, BalanceForm, LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Account, Category, Balance
from werkzeug.urls import url_parse
from sqlalchemy import func, and_
import calendar



# Quelle: Eigenentwicklung
@app.route('/')
@app.route('/index')
@login_required
def index():

    return render_template('index.html', title='Home')

# Quelle: Eigenentwicklung
@app.route('/data')
@login_required

def data():
    categories = Category.query.all()
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    years = get_years()
    months = get_months() 
    balances_by_year_month = {}
    
    for year in years:
        balances_by_month = {}
        for month in months:
            balances_for_month = Balance.query\
                .join(Account, Balance.account_id == Account.id)\
                .filter(Account.user_id == user_id, Balance.year == year, Balance.month == month)\
                .all()
            balances_by_month[month] = balances_for_month
        balances_by_year_month[year] = balances_by_month

    total_balances = {}
    for year in years:
        total_balances[year] = {}
        for month in months:
            month_balances = balances_by_year_month[year][month]
            if month_balances:
                total_balance = sum(balance.balance for balance in month_balances)
                total_balances[year][month] = total_balance
            else:
                total_balances[year][month] = None

    return render_template('data.html', title='Data', categories=categories, accounts=accounts, years=years, months=months, balances=balances_by_year_month, total_balances=total_balances)
def get_years():
    years = db.session.query(Balance.year).distinct().all()
    return [year[0] for year in years] 
def get_months():
    months = db.session.query(Balance.month).distinct().all()
    return [month[0] for month in months]

@app.route('/insert', methods=['GET', 'POST'])
@login_required
def insert():
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    form = BalanceForm(user_accounts=user_accounts)

    if form.validate_on_submit():
        account_id = form.account.data
        year = form.year.data
        month = form.month.data
        balance_value = form.balance.data

        # Validate for duplicates
        existing_balance = Balance.query.filter_by(account_id=account_id, year=year, month=month).first()
        if existing_balance:
            flash('A balance entry already exists for this account.')
            return redirect(url_for('insert'))

        # Get the Account instance based on the selected account_id
        account = Account.query.get(account_id)

        # Create a new Balance instance and set its attributes
        new_balance = Balance(account=account, balance=balance_value, year=year, month=month)

        # Add the new_balance instance to the database session
        db.session.add(new_balance)
        db.session.commit()

        flash('Balance inserted successfully!', 'success')
        return redirect(url_for('data'))

    accounts = Account.query.filter_by(user_id=current_user.id).all()
    form.account.choices = [(account.id, account.name) for account in accounts]

    form2 = AccountForm()

    if form2.validate_on_submit():
        category = form2.category.data
        account = form2.account.data
        user_id = current_user.id

        category = Category.query.get(category)
        #account = Account.query.get(account)

        new_account = Account(name=account, category=category, user_id=user_id)

        db.session.add(new_account)
        db.session.commit()

        flash('Account inserted successfully!', 'success')
        return redirect(url_for('insert'))

    categories = Category.query.all()
    form2.category.choices = [(category.id, category.name) for category in categories]

    return render_template('insert.html', title='Insert Balance', form=form, form2=form2)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    categories = Category.query.all()
    #user_id = current_user.id
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    years = get_years()
    months = get_months()
    balances_by_year_month = {}
    entries = Balance.query.join(Account).filter(Account.user_id == current_user.id).all()
    
    for year in years:
        balances_by_month = {}
        for month in months:
            balances_for_month = Balance.query\
                .join(Account, Balance.account_id == Account.id)\
                .filter(Account.user_id == current_user.id, Balance.year == year, Balance.month == month)\
                .all()
            balances_by_month[month] = balances_for_month
        balances_by_year_month[year] = balances_by_month

    
    
    return render_template('edit.html', title='Edit', entries=entries, categories=categories, accounts=accounts, years=years, months=months, balances=balances_by_year_month)
def get_years():
    years = db.session.query(Balance.year).distinct().all()
    return [year[0] for year in years] 
def get_months():
    months = db.session.query(Balance.month).distinct().all()
    return [month[0] for month in months]





@app.route('/balance/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_balance(id):
    balance = Balance.query.get_or_404(id)

    if not balance:
        # Handle entry not found
        return redirect(url_for('edit'))

    # Get updated values from the form
    new_balance = request.form.get('balance')
    new_year = request.form.get('year')
    new_month = request.form.get('month')

    print(f"New balance: {new_balance}, New year: {new_year}, New month: {new_month}")
  
    # Update the balance, year, and month
    balance.balance = new_balance
    balance.year = new_year
    balance.month = new_month

    #db.session.update(balance)
    db.session.commit()
    flash('Balance entry updated successfully!', 'success')
    return redirect(url_for('edit'))

@app.route('/balance/<int:id>/delete', methods=['GET', 'POST'])
@login_required
# Quelle: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/
def delete_balance(id):
    balance = Balance.query.get_or_404(id)
    db.session.delete(balance)
    db.session.commit()
    flash('Balance entry deleted successfully!', 'success')
    return redirect(url_for('edit'))

@app.route('/account/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_account(id):
    account = Account.query.get_or_404(id)

    if not account:
        return redirect(url_for('edit'))

    # Get values from form
    new_name = request.form.get('account')
    new_category = request.form.get('category')

    print(f"New name: {new_name}, New category: {new_category}")
  
    # Update name, category
    account.name = new_name
    account.category_id = new_category

    db.session.commit()
    flash('Account updated successfully!', 'success')
    return redirect(url_for('edit'))

@app.route('/account/<int:id>/delete', methods=['GET', 'POST'])
@login_required
# Quelle: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/
def delete_account(id):
    account = Account.query.get_or_404(id)
    balance_entries = Balance.query.filter_by(account_id=id).all()
    # Delete balance entries
    for balance_entry in balance_entries:
        db.session.delete(balance_entry)

    db.session.delete(account)
    db.session.commit()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('edit'))

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


@app.route('/api/users', methods=['GET'])
# Quelle: https://pythonbasics.org/flask-rest-api/
@login_required
def get_users():
    users = User.query.all()
    user_array = []

    for user in users:
        user_list = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        user_array.append(user_list)

    return jsonify(users=user_array)


@app.route('/api/accounts', methods=['GET'])
# Quelle: https://pythonbasics.org/flask-rest-api/
@login_required
def get_accounts():
    accounts = Account.query.all()
    account_array = []

    for account in accounts:
        account_list = {
            'id': account.id,
            'name': account.name,
            'user': account.user_id
        }
        account_array.append(account_list)

    return jsonify(accounts=account_array)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))