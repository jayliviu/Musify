from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length, InputRequired


class SignUpForm(FlaskForm):
    """Form for signing up users."""

    username = StringField('Create username', validators=[DataRequired()])
    password = PasswordField('Create password', validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Enter your username', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired()])


class SpotifySearchForm(FlaskForm):
    """Form to search for a spotify song."""

    search_query = StringField('search for music', validators=[InputRequired()])


class CreatePlaylistForm(FlaskForm):
    """Form for creating playlists."""

    playlist_name = StringField('name your playlist', validators=[InputRequired()])




