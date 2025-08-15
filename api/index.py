#!/usr/bin/env python3
"""
NeverPay2Spotify - Vercel Serverless Function
A serverless version of the Spotify to YouTube Music playlist transfer app.
"""

import os
import json
import re
import requests
from urllib.parse import urlparse, parse_qs
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def extract_playlist_id_from_url(spotify_url):
    """Extract playlist ID from Spotify URL"""
    if 'spotify.com/playlist/' in spotify_url:
        # Extract playlist ID from URL
        match = re.search(r'playlist/([a-zA-Z0-9]+)', spotify_url)
        if match:
            return match.group(1)
    return None

def search_youtube_music(ytm, query, max_results=5):
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

def get_html_template():
    """Get the HTML template content"""
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback HTML if template not found
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeverPay2Spotify - Transfer Playlists</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin-bottom: 20px; }
        input, textarea { width: 100%; padding: 10px; margin-top: 5px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 NeverPay2Spotify</h1>
        <p>Transfer your Spotify playlists to YouTube Music!</p>
        
        <form id="transferForm">
            <div class="form-group">
                <label for="spotifyUrl">Spotify Playlist URL:</label>
                <input type="url" id="spotifyUrl" required placeholder="https://open.spotify.com/playlist/...">
            </div>
            
            <div class="form-group">
                <label for="ytmusicHeaders">YouTube Music Headers (JSON):</label>
                <textarea id="ytmusicHeaders" rows="10" required placeholder='{"Cookie": "your-cookie-here", ...}'></textarea>
            </div>
            
            <div class="form-group">
                <label for="spotifyClientId">Spotify Client ID (optional):</label>
                <input type="text" id="spotifyClientId" placeholder="Your Spotify Client ID">
            </div>
            
            <div class="form-group">
                <label for="spotifyClientSecret">Spotify Client Secret (optional):</label>
                <input type="password" id="spotifyClientSecret" placeholder="Your Spotify Client Secret">
            </div>
            
            <button type="submit">Transfer Playlist</button>
        </form>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        document.getElementById('transferForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.className = 'result';
            resultDiv.innerHTML = 'Transferring... Please wait.';
            
            try {
                const response = await fetch('/transfer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        spotify_url: document.getElementById('spotifyUrl').value,
                        ytmusic_headers: JSON.parse(document.getElementById('ytmusicHeaders').value),
                        spotify_client_id: document.getElementById('spotifyClientId').value || null,
                        spotify_client_secret: document.getElementById('spotifyClientSecret').value || null
                    })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>Error:</strong> ${result.error}`;
                } else {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <strong>Success!</strong><br>
                        Playlist: ${result.playlist_name}<br>
                        Total tracks: ${result.total_tracks}<br>
                        Transferred: ${result.transferred_count}<br>
                        YouTube Music Playlist ID: ${result.ytm_playlist_id}
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        });
    </script>
</body>
</html>
        """

# Vercel entry point
def handler(request, context):
    """Vercel serverless function entry point"""
    try:
        # Parse the request
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        headers = request.get('headers', {})
        body = request.get('body', '')
        
        # Handle the request
        if method == 'GET' and path == '/':
            # Return the HTML template
            content = get_html_template()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': content
            }
        
        elif method == 'POST' and path == '/transfer':
            try:
                # Parse JSON data
                data = json.loads(body)
                
                spotify_url = data.get('spotify_url')
                ytmusic_headers = data.get('ytmusic_headers')
                spotify_client_id = data.get('spotify_client_id')
                spotify_client_secret = data.get('spotify_client_secret')
                
                if not spotify_url or not ytmusic_headers:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type'
                        },
                        'body': json.dumps({"error": "Missing required parameters"})
                    }
                
                # Perform the transfer
                result = transfer_playlist(
                    spotify_url, 
                    ytmusic_headers, 
                    spotify_client_id, 
                    spotify_client_secret
                )
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps(result)
                }
                
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps({"error": str(e)})
                }
        
        elif method == 'OPTIONS':
            # Handle CORS preflight requests
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'text/plain',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': 'Not Found'
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({"error": f"Internal server error: {str(e)}"})
        }
