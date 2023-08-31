import calendar
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

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

class BalanceForm(FlaskForm):
    balance = FloatField('Balance', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)], default=2023)
    #month = SelectField('Month', choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], validators=[DataRequired()])
    month_choices = [(str(month_num), month_name) for month_num, month_name in enumerate(calendar.month_name[1:], start=1)]
    month = SelectField('Month', choices=month_choices, validators=[DataRequired()])
    # Quelle: https://stackoverflow.com/questions/13964152/not-a-valid-choice-for-dynamic-select-field-wtforms
    account = SelectField('Account', choices=[], coerce=int, validators=[DataRequired()], validate_choice=False)
    submit = SubmitField('Submit')

class AccountForm(FlaskForm):
    account = StringField('Account Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()], validate_choice=False)
    submit = SubmitField('Submit')

