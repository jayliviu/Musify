from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


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
    spotify_id = db.Column(db.Text, nullable=False)
    spotify_uri = db.Column(db.Text, nullable=False)
    display_name = db.Column(db.Text, unique=True, nullable=False)
    country = db.Column(db.Text, nullable=True)
    external_urls = db.Column(db.Text, nullable=False)
    spotify_followers = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    token_expire_time = db.Column(db.Int, default=3600)

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

    likes = db.relationship(
        'Track', 
        secondary='likes'
    )

    playlists = db.relationship('Playlist', secondary='user_playlists')

    def __repr__(self):
        return f"<User id:{self.id}, name:{self.display_name}, spotify_id:{self.spotify_id}, spotify_uri:{self.spotify_uri}>"



class Playlist(db.Model):

    __tablename__ = 'playlists'

    id = db.Column(db.Int, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    playlist_owner = db.Column(db.Int, db.ForeignKey('users.id'))

    tracks = db.relationship('Track', secondary='PlaylistTrack', backref='playlists')

    def __repr__(self):
        return f"<Playlist id:{self.id}, name:{self.name}>"

    
class Track(db.Model):

    __tablename__ = 'tracks'

    id = db.Column(db.Int, primary_key=True, autoincrement=True)
    spotify_id = db.Column(db.Text, nullable=False)
    spotify_uri = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    popularity = db.Column(db.Int, nullable=True)
    duration_ms = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f"<Track id:{self.id}, spotify_id:{self.spotify_id}, spotify_uri:{self.spotify_uri}>"


class Artist(db.Model):

    __tablename__ = 'artists'

    id = db.Column(db.Int, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Artist id:{self.id}, name:{self.name}>"


class UserPlaylist(db.Model):

    __tablename__ = 'users_playlists'

    playlist_id = db.Column(db.Int, db.ForeignKey('playlists.id', primary_key=True))
    user_id = db.Column(db.Int, db.ForeignKey('users.id', primary_key=True))


class UserArtist(db.Model):

    __tablename__ = 'users_artists'

    artists_id = db.Column(db.Int, db.ForeignKey('artists.id', primary_key=True, ondelte='cascade'))
    users_id = db.Column(db.Int, db.ForeignKey('users.id', ondelte='cascade'))
        

class PlaylistTrack(db.Model):

    __tablename__ = 'playlists_tracks'

    playlist_id = db.Column(db.Int, db.ForeignKey('playlists.id', primary_key=True))
    track_id = db.Column(db.Int, db.ForeignKey('tracks.id', primary_key=True))


class Likes(db.Model):

    __tablename__ = 'likes'

    id = db.Column(db.Int, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Int, db.ForeignKey('users.id', ondelete='cascade'))
    track_id = db.Column(db.Int, db.ForeignKey('tracks.id', ondelete='cascade'))


    def __repr__(self):
        return f"<Like id:{self.id}, user_id:{self.user_id}, track_id:{self.track_id}>"