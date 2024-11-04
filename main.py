import os
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

# Load IDs from .env file
load_dotenv()

# Get variables from env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "http://spotify-analyzer-777.streamlit.app/callback"

# Check if CLIENT_ID and CLIENT_SECRET are loaded correctly
if CLIENT_ID is None or CLIENT_SECRET is None:
    st.error("Missing CLIENT_ID or CLIENT_SECRET. Please check your environment variables.")
else:
    st.write("Starting Spotify authentication process...")

    # Spotify API authentication
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope="user-top-read")

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        st.write(f"Please authorize access by visiting this URL: [Authorize Spotify]({auth_url})")
        auth_code = st.text_input("Enter the URL you were redirected to: ", value="")
        if auth_code:
            token_info = sp_oauth.get_access_token(auth_code)
            sp = spotipy.Spotify(auth=token_info['access_token'])
            st.write("Authorization successful! You can now see your top tracks.")
        else:
            sp = None
    else:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        st.write("You are already authorized. Here are your top tracks.")

    if sp:
        st.write("Retrieving data...")

        # Get user top tracks and popularity
        top_tracks = sp.current_user_top_tracks(limit=20)
        # Create DataFrame
        tracks_data = [{'name': track['name'], 'popularity': track['popularity']} for track in top_tracks['items']]
        df_tracks = pd.DataFrame(tracks_data)

        # Display top tracks in Streamlit
        st.title("Spotify Analyzer")
        st.header("Your Top Tracks")
        st.dataframe(df_tracks)

        # Plot popularity of top tracks
        fig, ax = plt.subplots()
        sns.barplot(x='popularity', y='name', data=df_tracks, ax=ax)
        st.pyplot(fig)

        # Get top artists and images
        top_artists = sp.current_user_top_artists(limit=10)
        artist_data = [{'name': artist['name'], 'image_url': artist['images'][0]['url']} for artist in top_artists['items']]

        # Display top artists in Streamlit
        st.header("Your Top Artists")
        for artist in artist_data:
            st.image(artist['image_url'], caption=artist['name'], width=150)
