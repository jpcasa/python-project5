from flask_wtf import Form
from wtforms import (StringField, PasswordField, TextAreaField,
                     IntegerField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange


class LoginForm(Form):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ])
    password = PasswordField(
        "Password",
         validators=[
             DataRequired()
         ])


class NewEntryForm(Form):
    title = StringField(
        "Title",
        validators=[
            DataRequired()
        ])
    date = DateField(
        "Date",
        format='%Y-%m-%d',
        validators=[
            DataRequired()
        ])
    timeSpent = IntegerField(
        "Time Spent (In Minutes)",
         validators=[
             DataRequired(),
             NumberRange(min=0)
         ])
    whatILearned = TextAreaField(
        "What I Learned",
         validators=[
             DataRequired()
         ])
    resourcesToRemember = TextAreaField(
        "Resources to Remember",
         validators=[
             DataRequired()
         ])
    tags = StringField(
        "Tags (Optional). Separate tags with a comma (,)!")
