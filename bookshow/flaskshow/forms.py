from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,IntegerField,DateField, FileField,DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed
from flask_wtf.csrf import CSRFProtect




class BuyerRegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class AdminRegistrationForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired(), NumberRange(min=1, message="Please enter a valid ID.")])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    venue_id = IntegerField('Venue ID')
    submit = SubmitField('Sign Up')


class BuyerLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class VenueForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=50)])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    venue_id = IntegerField('VenueID', validators=[InputRequired(False)])
    submit = SubmitField('Submit')


class EventForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    venue = SelectField('Venue', choices=[], validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()])
    end_time = StringField('End Time', validators=[DataRequired()])
    ticket_price = DecimalField('Ticket Price', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Submit')

    class Meta:
        csrf = True


class DeleteVenueForm(FlaskForm):
    id = IntegerField('ID')
    submit = SubmitField('Delete')
    
    class Meta:
        csrf = True

class DeleteShowForm(FlaskForm):
    id = IntegerField('ID')
    submit = SubmitField('Delete')

    class Meta:
        csrf = True        

class EditVenueForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=50)])
    capacity = StringField('Capacity', validators=[DataRequired(), Length(min=1, max=4)])
    submit = SubmitField('Edit')

class BuyTicketForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy Ticket')




