#!/usr/bin/env python3
"""
NeverPay2Spotify - Transfer Spotify playlists to YouTube Music
A local web application for migrating playlists between music services.
"""

import os
import json
import re
import requests
from urllib.parse import urlparse, parse_qs
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_playlist_id_from_url(spotify_url):
    """Extract playlist ID from Spotify URL"""
    if 'spotify.com/playlist/' in spotify_url:
        # Extract playlist ID from URL
        match = re.search(r'playlist/([a-zA-Z0-9]+)', spotify_url)
        if match:
            return match.group(1)
    return None

def search_youtube_music(ytmusic, query, max_results=5):
    """Search for a song on YouTube Music and return the best match"""
    try:
        results = ytm.search(query, filter="songs", limit=max_results)
        if results and len(results) > 0:
            # Return the first result (best match)
            return results[0].get('videoId')
    except Exception as e:
        print(f"Error searching YouTube Music: {e}")
    return None

def transfer_playlist(spotify_playlist_url, ytmusic_headers, spotify_client_id=None, spotify_client_secret=None):
    """Transfer a Spotify playlist to YouTube Music"""
    try:
        # Initialize YouTube Music
        ytm = YTMusic(ytmusic_headers)
        
        # Initialize Spotify client
        if spotify_client_id and spotify_client_secret:
            sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=spotify_client_id,
                    client_secret=spotify_client_secret
                )
            )
        else:
            # Try to use environment variables
            sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        
        # Extract playlist ID from URL
        playlist_id = extract_playlist_id_from_url(spotify_playlist_url)
        if not playlist_id:
            return {"error": "Invalid Spotify playlist URL"}
        
        # Get Spotify playlist details
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        playlist_description = f"Transferred from Spotify playlist: {playlist_name}"
        
        # Get all tracks from the playlist
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        
        while results['next']:
            results = sp.playlist_tracks(playlist_id, offset=len(tracks))
            tracks.extend(results['items'])
        
        # Create YouTube Music playlist
        ytm_playlist_id = ytm.create_playlist(
            title=playlist_name,
            description=playlist_description,
            privacy_status="PRIVATE"
        )
        
        # Transfer tracks
        transferred_count = 0
        failed_tracks = []
        video_ids = []
        
        for track in tracks:
            if track['track']:
                track_name = track['track']['name']
                artists = [artist['name'] for artist in track['track']['artists']]
                search_query = f"{track_name} {' '.join(artists)}"
                
                # Search for the song on YouTube Music
                video_id = search_youtube_music(ytm, search_query)
                
                if video_id:
                    video_ids.append(video_id)
                    transferred_count += 1
                else:
                    failed_tracks.append({
                        'name': track_name,
                        'artists': artists
                    })
        
        # Add all found songs to the playlist
        if video_ids:
            ytm.add_playlist_items(ytm_playlist_id, video_ids)
        
        return {
            "success": True,
            "playlist_name": playlist_name,
            "total_tracks": len(tracks),
            "transferred_count": transferred_count,
            "failed_tracks": failed_tracks,
            "ytm_playlist_id": ytm_playlist_id
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer', methods=['POST'])
def transfer():
    try:
        data = request.get_json()
        spotify_url = data.get('spotify_url')
        ytmusic_headers = data.get('ytmusic_headers')
        spotify_client_id = data.get('spotify_client_id')
        spotify_client_secret = data.get('spotify_client_secret')
        
        if not spotify_url or not ytmusic_headers:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Parse YouTube Music headers
        try:
            if isinstance(ytmusic_headers, str):
                ytmusic_headers = json.loads(ytmusic_headers)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid YouTube Music headers format"}), 400
        
        # Perform the transfer
        result = transfer_playlist(
            spotify_url, 
            ytmusic_headers, 
            spotify_client_id, 
            spotify_client_secret
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_headers', methods=['POST'])
def upload_headers():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            with open(filepath, 'r') as f:
                headers = json.load(f)
            return jsonify({"headers": headers})
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON file"}), 400
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
