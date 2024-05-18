"""
This Flask web application provides a simple interface for users to view their Spotify playlists.

The application uses the Spotipy library to authenticate with the Spotify API and retrieve the user's playlists. The authentication process is handled using the SpotifyOAuth class, which provides a way to obtain an access token from the Spotify API.

The main routes in the application are:

- `home()`: Checks if the user has a valid access token, and if not, redirects the user to the Spotify authorization page.
- `callback()`: Handles the callback from the Spotify authorization page, obtaining an access token and redirecting the user to the `get_playlists()` route.
- `get_playlists()`: Retrieves the user's playlists from the Spotify API and displays them on the web page.
- `logout()`: Clears the user's session and redirects the user to the home page.

The application uses the Flask-Session cache handler to store the user's access token, which allows the user to remain authenticated across multiple requests.
"""
import os
from flask import Flask, session, url_for, request ,redirect
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

"""
Configures the Spotify OAuth2 authentication flow for the application.

The `client_id` and `client_secret` are the unique identifiers for the Spotify application.
The `redirect_uri` is the URL that Spotify will redirect the user to after they have authenticated.
The `scope` parameter specifies the permissions that the application is requesting from the user.
The `cache_handler` is used to store the user's access token and refresh token, so that the user
doesn't have to re-authenticate every time they use the application.
The `sp_oauth` object is used to manage the OAuth2 flow, and the `sp` object is used to make
API calls to Spotify on behalf of the authenticated user.
"""

client_id = os.environ.get('Client_ID_Spot')
client_secret = os.environ.get('Client_Secret_Spot')


redirect_uri = 'http://localhost:5000/callback'

scope = 'playlist-read-private'

cache_handler= FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(client_id=client_id, 
                        client_secret=client_secret, 
                        redirect_uri=redirect_uri, 
                        scope=scope, 
                        cache_handler=cache_handler,
                        show_dialog=True)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    playlists = sp.current_user_playlists()
    if playlists is not None:
        playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
        playlists_html= '<br>'.join([f'{name}: {url}' for name, url in playlists_info])
        return playlists_html
    else:
        return "No playlists found"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
    
