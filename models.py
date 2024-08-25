from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()



class Follows(db.Model):
    
    __tablename__ = 'follows'

    user_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )


class User(db.Model):
    
    __tablename__ = 'users'

    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    spotify_id = db.Column(db.Text, nullable=True)
    spotify_uri = db.Column(db.Text, nullable=True)
    display_name = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    external_urls = db.Column(db.Text, nullable=True)
    spotify_followers = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    token_expire_time = db.Column(db.DateTime, nullable=True)

    musify_followers = db.relationship(
        'User',
        secondary='follows',
        primaryjoin=(Follows.user_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    musify_following = db.relationship(
        'User',
        secondary='follows',
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_followed_id == id)
    )

    def __repr__(self):
        return f"User(id={self.id}, display_name={self.display_name}, spotify_id={self.spotify_id}, spotify_uri={self.spotify_uri})"

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    
    def serialize_user(self):
        """Returns python dictionary of User object."""

        return {
            'id' : self.id,
            'username' : self.username,
            'display_name' : self.display_name,
            'country' : self.country,
            'spotify_id' : self.spotify_id,
            'spotify_uri' : self.spotify_uri,
            'external_urls' : self.external_urls,
            'image_url' : self.image_url,
            'spotify_followers' : self.spotify_followers
        }

    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Playlist(db.Model):

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    date_created = db.Column(db.Text, default=str(datetime.now()))

    #Many-to-One with Users
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='playlists')

    tracks = db.relationship('LikedTrack', secondary='playlists_tracks', backref='playlists')


    def __repr__(self):
        return f"Playlist(id={self.id}, name={self.name}, date_created={self.date_created}, user_id={self.user_id})"
    
    def serialize_playlist(self):
        """Returns python dictionary of Playlist object."""

        return {
            "id"          : self.id,
            "name"        : self.name,
            "date_created": self.date_created,
            "user_id"     : self.user_id
        }

    
class LikedTrack(db.Model):
    
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    spotify_id = db.Column(db.Text, nullable=False)
    spotify_uri = db.Column(db.Text, nullable=False)
    date_liked = db.Column(db.Text, default=str(datetime.now()))
    artist_name = db.Column(db.Text, nullable=False)
    artist_url = db.Column(db.Text, nullable=False)

    #Many-to-One with Users
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='tracks')


    def __repr__(self):
        return f"LikedTrack(id={self.id}, spotify_id={self.spotify_id}, spotify_uri={self.spotify_uri}, date_liked={self.date_liked}, user_id={self.user_id})"
    

    def serialize_liked_track(self):
        """Returns python dictionary of LikedTrack object."""

        return {
            "id" : self.id,
            "name" : self.name,
            "spotify_id" : self.spotify_id,
            "spotify_uri" : self.spotify_uri,
            "date_liked" : self.date_liked,
            "artist_name" : self.artist_name,
            "artist_url" : self.artist_url,
            "user_id" : self.user_id
        }
    

class PlaylistTrack(db.Model):
    """Connects Playlist and LikedTracks"""

    __tablename__ = 'playlists_tracks'

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete='cascade'), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id', ondelete='cascade'), primary_key=True)

    def __repr__(self):
        return f"PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id})"
    
