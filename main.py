import os
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Load IDs from .env file
load_dotenv()

# Get variables from env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "https://spotify-analyzer-777.streamlit.app"

# Check if CLIENT_ID and CLIENT_SECRET are loaded correctly
if CLIENT_ID is None or CLIENT_SECRET is None:
    st.error("Missing CLIENT_ID or CLIENT_SECRET. Please check your environment variables.")
else:
    # Spotify API authentication
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope="user-read-currently-playing user-top-read")

    # Check the URL parameters for the authorization code
    query_params = st.experimental_get_query_params()
    auth_code = query_params.get("code", None)

    if auth_code:
        try:
            token_info = sp_oauth.get_access_token(auth_code[0], as_dict=False)
            sp = spotipy.Spotify(auth=token_info)
            st.success("Authorization successful! You can now see your data.")
        except Exception as e:
            st.error(f"Error: {e}")
        sp = None
    else:
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            auth_url = sp_oauth.get_authorize_url()
            st.write(f"Please authorize access by visiting this URL: [Authorize Spotify]({auth_url})")
            sp = None
        else:
            sp = spotipy.Spotify(auth=token_info['access_token'])

    if sp:
        # Create a sidebar dropdown navigation menu
        menu = st.sidebar.selectbox("Select a section", ["Top Tracks", "Top Artists", "Currently Playing"])

        if menu == "Top Tracks":
            st.header("Your Top Tracks")
            # Create data frame
            top_tracks = sp.current_user_top_tracks(limit=20)
            tracks_data = [{'name': track['name'], 'popularity': track['popularity']} for track in top_tracks['items']]
            df_tracks = pd.DataFrame(tracks_data)

            # Create Plot
            plt.figure(figsize=(10, 6))
            sns.set(style="whitegrid")
            bar_plot = sns.barplot(x='name', y='popularity', data=df_tracks, palette="viridis")
            bar_plot.set_title("Your Top 20 Tracks and their Popularity")
            bar_plot.set_xlabel("Track Name")
            bar_plot.set_ylabel("Popularity")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(plt)

        elif menu == "Top Artists":
            st.header("Your Top 10 Artists")
            # Get top artists and images
            top_artists = sp.current_user_top_artists(limit=10)
            artist_data = [{'name': artist['name'], 'image_url': artist['images'][0]['url']} for artist in top_artists['items']]
            # Display top artists in Streamlit
            for artist in artist_data:
                st.image(artist['image_url'], caption=artist['name'], width=400)

        elif menu == "Currently Playing":
            st.header("Current Playing")
            current_track = sp.current_user_playing_track()
            if current_track is not None:
                track_data = {
                    'name': current_track['item']['name'],
                    'artist': current_track['item']['artists'][0]['name'],
                    'album': current_track['item']['album']['name'],
                    'popularity': current_track['item']['popularity'],
                    'album_art': current_track['item']['album']['images'][0]['url']
                }
                st.image(track_data['album_art'], caption=track_data['name'], width=400)
                st.write(track_data['name'])
                st.write(track_data['artist'])
                st.write(track_data['album'])
            else:
                st.write("You are not listening to anything currently!")
