from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserRegisterForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('(Optional) Email', validators=[Optional(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[Length(min=6)])

class EditUserForm(FlaskForm):
    """ Form for editing users. """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('Bio')


class UserLoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class SearchForm(FlaskForm):
    """ Search Form. """

    englishTitle = StringField('English Title...')