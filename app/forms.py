import calendar
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from app.models import User, Balance

# Form for user login, Quelle: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Form for user registration, Quelle: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Form for adding new balances, Quelle: Eigenentwicklung
class BalanceForm(FlaskForm):
    account = SelectField('Account', choices=[], coerce=int, validators=[DataRequired()], validate_choice=False)
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)], default=2023)
    month_choices = [(str(month_num), month_name) for month_num, month_name in enumerate(calendar.month_name[1:], start=1)]
    # SelectField, Quelle: https://stackoverflow.com/questions/13964152/not-a-valid-choice-for-dynamic-select-field-wtforms
    month = SelectField('Month', choices=month_choices, validators=[DataRequired()])
    balance = FloatField('Balance', validators=[DataRequired(), NumberRange(min=-99999999, max=999999999)])
    # Function for not allowing duplicate balance entries for selected month
    def validate_duplicates(self, account, year, month):
        existing_balance = Balance.query.filter_by(account_id=account, year=year, month=month).first()
        if existing_balance:
            raise ValidationError(f"A balance entry for {calendar.month_name[month]} {year} already exists for this account.")
    submit = SubmitField('Submit')

# Form for adding new accounts, Quelle: Eigenentwicklung
class AccountForm(FlaskForm):
    account = StringField('Account Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()], validate_choice=False)
    submit = SubmitField('Submit')

