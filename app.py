from flask import Flask, redirect, session, render_template, flash, request
from models import db, connect_db, User, Follows
import requests
import string
import secrets
from urllib.parse import urlencode
from base64 import b64encode, b64decode
from flask_debugtoolbar import DebugToolbarExtension
from secret import SECRET, CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, AUTHORIZE_URL, TOKEN_URL, API_BASE_URL


app = Flask(__name__)
app.debug = True


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///musify'
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = SECRET


connect_db(app)
toolbar = DebugToolbarExtension(app)

#Generate random state to check ensure it is the same user who was redirected back to our app after authorizing Musify access to their spotify account
alphabet = string.ascii_letters + string.digits
random_state = ''.join(secrets.choice(alphabet) for i in range(10))

#Base64 encode my client_id and client_secret
client_id_secret = CLIENT_ID + ':' + CLIENT_SECRET
client_id_secret_encoded = b64encode(client_id_secret.encode('utf-8'))
client_id_secret_b64 = b64decode(client_id_secret_encoded)



def refresh_tok(refresh_tok):
    """Refresh a users expired access token"""

    params = {
        'grant_type'   : 'refresh_token',
        'refresh_token': refresh_tok,
    }

    headers = {
        'Authorization': client_id_secret_b64
    }

    request = requests.post(TOKEN_URL, headers=headers, data=params)
    
    if request.status_code == 200:
        request_data = request.json()
        access_token = request_data['access_token']
        token_type = request_data['token_type']
        expires_in = request_data['expires_in']
        refresh_token = request_data['refresh_token']



@app.route('/', methods=['GET'])
def show_homepage():
    return render_template('home.html')


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
      'show_dialog'  : False
   }

   authorization_url = f"{AUTHORIZE_URL}?{urlencode(params)}"

   return redirect(authorization_url)


@app.route('/callback')
def signup_user():
    """Save user's profile information upon returning to our app after authorization."""
    
    state = request.args['state']
    if state == random_state:
        
        code = request.args['code']

        headers = {
            "Authorization" : client_id_secret_b64
        }

        params = {
            'grant_type'  : 'authorization_code',
            'code'        : code,
            'redirect_uri': REDIRECT_URL
        }
        
        request = requests.post(TOKEN_URL, headers=headers, data=params)
        
        if request.status_code == 200:
            request_data = request.json()
            access_token = request_data['access_token']
            token_type = request_data['token_type']
            expires_in = request_data['expires_in']
            refresh_token = request_data['refresh_token']



         

            
         










# @app.route('/authorization')
# def get_tok_for_signup():

#     if g.user:
#         flash('Looks like you are already signed up!', 'danger')
#         return redirect(f'/users/{g.user.id}')

   #  scopes = 'user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private user-follow-read user-follow-modify user-library-read user-library-modify playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played user-read-playback-position'   

   #  params = {
      # 'client_id': CLIENT_ID,
      # 'response_type': 'code',
      # 'redirect_uri': REDIRECT_URI,
      # 'state': STATE,
      # 'scope': scopes,
      # 'show_dialog': True
   #  }

   #  auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

#     return redirect(auth_url)


# @app.route('/callback')
# def callback():

#     if g.user:
#         flash("You cannot view this page!", "danger")
#         return redirect('/')
    
#     if 'error' in request.args:
#         flash(f"{request.args['error']}", "danger")
#         return redirect('/')
    
#     if 'code' in request.args and 'state' in request.args and STATE == request.args['state']:
        
#         params = {CLIENT_ID:CLIENT_SECRET}
#         code = request.args['code']

#         req_body = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': REDIRECT_URI,
#         }

#         client_info = CLIENT_ID + ':' + CLIENT_SECRET
#         client_info_b64 = base64.b64encode(client_info.encode()).decode()

#         headers = {
#             "Content-Type": "application/x-www-form-urlencoded",
#             "Authorization": "Basic " +  client_info_b64
#         }

#         response = requests.post(url=TOKEN_URL, data=urllib.parse.urlencode(req_body), headers=headers)
#         token_info = response.json()
#         print(token_info)

#         if 'code' in session and 'state' in session and 'access_token' in session and 'refresh_token' in session and 'expires_at' in session:
#             del session['code']
#             del session['state']
#             del session['access_token']
#             del session['refresh_token']
#             del session['expires_at']

#         session['code'] = request.args['code']
#         session['state'] = request.args['state']    
#         session['access_token'] = token_info['access_token']
#         session['refresh_token'] = token_info['refresh_token']
#         session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

#         return redirect('/signup')
#     else:
#         flash('Oops! Something went wrong please try again!', 'danger')
