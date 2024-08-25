from flask import Flask, redirect, session, render_template, flash, request, url_for, jsonify
from models import db, connect_db, User, Follows, PlaylistTrack, Playlist, LikedTrack
import requests
from sqlalchemy.exc import IntegrityError
import json
import string
import secrets
import urllib.parse
from base64 import b64encode, b64decode
from flask_debugtoolbar import DebugToolbarExtension
from secret import SECRET, CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, AUTHORIZE_URL, TOKEN_URL, API_BASE_URL
from datetime import datetime, timedelta
from forms import SignUpForm, LoginForm, SpotifySearchForm, CreatePlaylistForm


app = Flask(__name__)
app.debug = True


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///musify'
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = SECRET


connect_db(app)
toolbar = DebugToolbarExtension(app)

#Generate random state to ensure it is the same user who was redirected back to our app after authorizing Musify access to their spotify account
alphabet = string.ascii_letters + string.digits
random_state = ''.join(secrets.choice(alphabet) for i in range(10))


#Base64 encode client_id and client_secret
client_id_secret = CLIENT_ID + ':' + CLIENT_SECRET
client_id_secret_encoded = b64encode(client_id_secret.encode('utf-8'))
client_id_secret_b64 = client_id_secret_encoded.decode('utf-8')


# Commonly used functions in the app. 

def login(user):
     session['user'] = user.id


def logout():
	del session['user']


def refresh_user_access_token(refresh_token):
    """Refresh a users expired access token."""

    user = User.query.get_or_404(session['user'])

    refresh_token_headers = {
         'Content-Type'   : 'application/x-www-form-urlencoded',
         'Authorization'  : 'Basic ' + client_id_secret_b64
    }
    
    params = {
         'grant_type':'refresh_token',
         'refresh_token':refresh_token,
    }
    
    refresh_token_url = f"{TOKEN_URL}?{urllib.parse.urlencode(params)}"

    refresh_token_response = requests.post(refresh_token_url, headers=refresh_token_headers)
    
    data = refresh_token_response.json()
    
    access_token = data.get('access_token')
    
    user.access_token = access_token
    
    user.token_expire_time = datetime.now() + timedelta(hours=1)
    
    db.session.commit()
    return
     


# User Routes 


@app.route('/', methods=['GET'])
def show_homepage():
    """Display Musify Homepage."""

    return render_template('home.html', random_state=random_state)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
     """Login User."""
     
     form = LoginForm()

     if form.validate_on_submit():
          username = form.username.data
          password = form.password.data
          user = User.authenticate(username=username, password=password)
          if user:
               login(user)
               flash(f"Welcome back, {user.display_name}!", "success")
               return redirect('/search')
          else:
               flash("We could not log you in based on those credentials, sorry!", "danger")
               return redirect('/login')
     else:
          return render_template('/authorization/login.html', form=form)
     

@app.route('/logout')
def logout_user():
     """Logout user."""
    
     if 'user' in session:
          logout()
     
     return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def show_signup():
	"""Route for signing up a user to our app."""
        
	form = SignUpForm()
        
	if form.validate_on_submit():
		try:
			username = form.username.data
			password = form.password.data
			user = User.signup(username=username, password=password)
			db.session.commit()
			login(user)
			return redirect('/authorization')

		except IntegrityError as e:
			flash('This username is already taken and signed up!', 'danger')
			return redirect('signup')
                
	else:
		return render_template('/authorization/signup.html', form=form)




@app.route('/authorization')
def request_authorization():
   """Get user authorization to modify Spotify account."""
    
   scopes = 'user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private user-follow-read user-follow-modify user-library-read user-library-modify playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-position'

   params = {
      'client_id'    : CLIENT_ID,
      'response_type': 'code',
      'redirect_uri' : REDIRECT_URL,
      'state'        : random_state,
      'scope'        : scopes,
      'show_dialog'  : True
   }
   auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

   return redirect(auth_url)


@app.route('/callback')
def complete_user_signup():
    """Save user's profile information upon returning to our app after authorization."""
    
    if 'error' in request.args:
         return redirect('/')
    
    elif 'code' in request.args and 'state' in request.args and random_state == request.args['state']:

        code = request.args['code']
        
        token_headers = {
            "Authorization" : 'Basic ' + client_id_secret_b64
        }
        
        token_params = {
            'grant_type'  : 'authorization_code',
            'code'        : code,
            'redirect_uri': REDIRECT_URL
        }
        
        token_response = requests.post(TOKEN_URL, headers=token_headers, data=token_params)

        if token_response.status_code == 200:
             
             data = token_response.json()
             access_token = data.get('access_token')
             refresh_token = data.get('refresh_token')
             token_expire_time = datetime.now() + timedelta(hours=1)
        else:
             
             return redirect('/')

        profile_header = {
            'Authorization': f"Bearer {access_token}"
        }
        
        profile_response = requests.get('https://api.spotify.com/v1/me', headers=profile_header)

        if profile_response.status_code == 200:
             
             data = profile_response.json()
             
             spotify_id = data.get('id', '')
             spotify_uri = data.get('uri', '')
             display_name = data.get('display_name', '')
             country = data.get('country', '')
             image_url = data.get('images')[0].get('url', '')
             external_urls = data.get('external_urls').get('spotify', '')
             spotify_followers = data.get('followers').get('total', 0)
             
             user = User.query.get_or_404(session['user'])
             
             user.spotify_id = spotify_id
             user.spotify_uri = spotify_uri
             user.display_name = display_name
             user.country = country
             user.external_urls = external_urls
             user.image_url = image_url
             user.spotify_followers = spotify_followers
             user.access_token = access_token
             user.refresh_token = refresh_token
             user.token_expire_time = token_expire_time
             
             db.session.commit()
             
             flash('Successfully Connected!', 'success')
             return redirect('/search')
        
        else:
             
             return redirect('/')
        


@app.route('/search', methods=['GET', 'POST'])
def search_song():
    """Route for displaying Musify search page and form, also handle POST requests from search for to display results.
     """
    
    if 'user' not in session:
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
    else:
          user = User.query.get_or_404(session['user'])

    if user.token_expire_time < datetime.now():
         refresh_user_access_token(user.refresh_token)
         
    search_form = SpotifySearchForm()
    
    if request.method == 'POST':
         
         try:

              data = json.loads(request.data)

              search_query = data.get('value')

              header = {
                   'Authorization': f'Bearer {user.access_token}'
			  }

              search_params = {
                   'q'      : search_query,
                   'type'   : 'track',
                   'limit'  : '40'
			  }

              search_url = f'https://api.spotify.com/v1/search?{urllib.parse.urlencode(search_params)}'

              spotify_search_response = requests.get(search_url, headers=header)

              search_data = spotify_search_response.json()

              items = search_data.get('tracks').get('items')

              return jsonify(items=items, user=user.serialize_user(), status='success')

         except:

              return redirect('/error')
         
         
    return render_template('search.html', search_form=search_form, user=user)



@app.route('/playlists', methods=['GET', 'POST'])
def show_playlists():
     """Route for displaying all of a users playlists. Also handle POST requests to create new playlists."""
     
     if 'user' not in session:
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
     else:
          user = User.query.get_or_404(session['user'])
	
     create_playlist_form = CreatePlaylistForm()
     
     playlists = user.playlists
     
     if request.method == 'POST':
          
          try:
               
               data = json.loads(request.data)
               
               playlist_name = data.get('playlist_name')
               
               user_id = data.get('user_id')
               
               date_created = str(datetime.now())
               
               playlist = Playlist(name=playlist_name, date_created=date_created, user_id=user_id)
               
               db.session.add(playlist)
               
               db.session.commit()
               
               commited_playlist = Playlist.query.filter((Playlist.name == playlist_name) & (Playlist.user_id == user_id) & (Playlist.date_created == date_created)).one()
               
               return jsonify(playlist=commited_playlist.serialize_playlist(), user=user.serialize_user(), status='success')
          
          except:
               
               return redirect('/error')
               
     return render_template('/playlists/playlists.html', user=user, create_playlist_form=create_playlist_form, playlists=playlists)
          

@app.route('/playlists/<int:id>', methods=['DELETE'])
def delete_playlist(id):
     """Route for deleting a user's playlist."""
     
     if 'user' not in session:          
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
     
     try:
          
          playlist = Playlist.query.get_or_404(id)

          db.session.delete(playlist)

          db.session.commit()

          return jsonify(status='success')

     except:

          return redirect('/error')
     

@app.route('/playlists/<int:id>/tracks', methods=['GET'])
def show_playlist_tracks(id):
     """Route for proving data so front-end javascript can display each track in a user playlist."""
     
     if 'user' not in session:
          flash('Please log in first!', 'danger')
          return redirect('/')
     else:
          user = User.query.get_or_404(session['user'])

     try:

          playlist = Playlist.query.get_or_404(id)

          tracks = [track.serialize_liked_track() for track in playlist.tracks]

          return jsonify(playlist=playlist.serialize_playlist(), tracks=tracks, user=user.serialize_user(), status='success')

     except:

          return redirect('/error')
          


@app.route('/add/playlists/tracks', methods=['POST'])
def add_track_to_playlist():
     """Route for commiting a new track to user playlist."""
     
     if 'user' not in session:
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
     
     try:

          data = json.loads(request.data)

          playlist = Playlist.query.get(data.get('playlist_id'))

          track = LikedTrack.query.get(data.get('track_id'))

          playlist.tracks.append(track)

          db.session.commit()
          
          return jsonify(status='success')

     except:

          return redirect('/error')
          


@app.route('/tracks', methods=['GET', 'POST'])
def get_liked_tracks():
     """Route for displaying all of a user's liked tracks and handling POST request for creating new liked tracks.
      """
     
     if 'user' not in session:
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
     else:
          user = User.query.get_or_404(session['user'])

     tracks = user.tracks
     
     if request.method == 'POST':
          
          try:
               
               data = json.loads(request.data)

               name = data.get('track_name')

               spotify_id = data.get('track_id')

               spotify_uri = data.get('track_uri')

               artist_name = data.get('track_artist_name')

               artist_url = data.get('track_artist_url')

               user_id = data.get('user_id')

               track = LikedTrack(name=name, spotify_id=spotify_id, spotify_uri=spotify_uri, artist_name=artist_name, artist_url=artist_url, user_id=user_id)

               db.session.add(track)

               db.session.commit()

               new_track = LikedTrack.query.filter((LikedTrack.spotify_id == spotify_id) & (LikedTrack.user_id == user_id)).one()
               
               track_id = new_track.id

               return jsonify(track=track_id)
          
          except:
               return redirect('/error')
          
          
     return render_template('/tracks/tracks.html', tracks=tracks, user=user)



@app.route('/tracks/<int:id>', methods=['DELETE'])
def remove_from_likes(id):
     """Route for deleting a track from user's liked tracks."""
     
     if 'user' not in session:
          flash(f"Uh Oh! You need to login!", "danger")
          return redirect('/')
     
     try:

          track = LikedTrack.query.get_or_404(id)

          db.session.delete(track)

          db.session.commit()
          
          return jsonify(status='success')

     except:

          return redirect('/error')



@app.route('/playlists/data', methods=['GET'])     
def get_playlist_data():
     """Route for returning user's playlists data that they may add a track to their playlists."""
     
     if 'user' not in session:
          flash(f"Please Login First!", "danger")
          return redirect('/')
     else:
          user = User.query.get_or_404(session['user'])
          
     try:

          playlists = user.playlists

          return jsonify(playlists=[playlist.serialize_playlist() for playlist in playlists], user=user.serialize_user(), status='success')

     except:

          return redirect('/error')
          



@app.route('/tracks/date', methods=['POST'])
def get_tracks_by_date():
     """Route for handling POST requests for getting each track a user liked based on a date."""
     
     if 'user' not in session:
          flash('Please log in first!', 'danger')
          return redirect('/')
     else:
          user = User.query.get_or_404(session['user'])

     try:

          data = json.loads(request.data)

          date_string = str(data.get('date_liked'))

          date_object = datetime.strptime(date_string, "%Y-%m-%d")

          date_liked = date_object.strftime("%Y-%m-%d")

          tracks_by_date = LikedTrack.query.filter((LikedTrack.user_id == user.id) & (LikedTrack.date_liked.like(f"{date_liked}%"))).all()

          serialized_tracks_by_date = [track.serialize_liked_track() for track in tracks_by_date]

          return jsonify(tracks=serialized_tracks_by_date, status='success')

     except:

          return redirect('/error')


@app.route('/error', methods=['GET'])
def handle_error_page():
     return render_template('error_page.html')

     


     