#!/usr/bin/env python3
"""
NeverPay2Spotify - Vercel Serverless Function
A serverless version of the Spotify to YouTube Music playlist transfer app.
"""

import json
import re
import os
from http.server import BaseHTTPRequestHandler
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def extract_playlist_id_from_url(spotify_url):
    """Extract playlist ID from Spotify URL"""
    if 'spotify.com/playlist/' in spotify_url:
        match = re.search(r'playlist/([a-zA-Z0-9]+)', spotify_url)
        if match:
            return match.group(1)
    return None

def search_youtube_music(ytm, query, max_results=5):
    """Search for a song on YouTube Music and return the best match"""
    try:
        results = ytm.search(query, filter="songs", limit=max_results)
        if results and len(results) > 0:
            return results[0].get('videoId')
    except Exception as e:
        print(f"Error searching YouTube Music: {e}")
    return None

def test_youtube_music_headers(ytmusic_headers):
    """Test if YouTube Music headers are valid"""
    try:
        ytm = YTMusic(ytmusic_headers)
        # Try to get user info to test authentication
        user_info = ytm.get_user_info()
        return {"success": True, "user_info": user_info}
    except Exception as e:
        return {"error": str(e)}

def transfer_playlist(spotify_playlist_url, ytmusic_headers, spotify_client_id=None, spotify_client_secret=None):
    """Transfer a Spotify playlist to YouTube Music"""
    try:
        print(f"Starting transfer for URL: {spotify_playlist_url}")
        print(f"Headers provided: {list(ytmusic_headers.keys())}")
        
        # Initialize YouTube Music with provided headers
        try:
            ytm = YTMusic(ytmusic_headers)
            print("YouTube Music client initialized successfully")
        except Exception as e:
            print(f"Error initializing YouTube Music: {e}")
            return {"error": f"YouTube Music initialization failed: {str(e)}"}
        
        # Initialize Spotify client
        try:
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
            print("Spotify client initialized successfully")
        except Exception as e:
            print(f"Error initializing Spotify: {e}")
            return {"error": f"Spotify initialization failed: {str(e)}"}
        
        # Extract playlist ID from URL
        playlist_id = extract_playlist_id_from_url(spotify_playlist_url)
        if not playlist_id:
            return {"error": "Invalid Spotify playlist URL"}
        
        print(f"Extracted playlist ID: {playlist_id}")
        
        # Get Spotify playlist details
        try:
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist['name']
            playlist_description = f"Transferred from Spotify playlist: {playlist_name}"
            print(f"Playlist name: {playlist_name}")
        except Exception as e:
            print(f"Error getting playlist details: {e}")
            return {"error": f"Failed to get playlist details: {str(e)}"}
        
        # Get all tracks from the playlist
        try:
            tracks = []
            results = sp.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            
            while results['next']:
                results = sp.playlist_tracks(playlist_id, offset=len(tracks))
                tracks.extend(results['items'])
            
            print(f"Found {len(tracks)} tracks in playlist")
        except Exception as e:
            print(f"Error getting tracks: {e}")
            return {"error": f"Failed to get playlist tracks: {str(e)}"}
        
        # Create YouTube Music playlist
        try:
            ytm_playlist_id = ytm.create_playlist(
                title=playlist_name,
                description=playlist_description,
                privacy_status="PRIVATE"
            )
            print(f"Created YouTube Music playlist with ID: {ytm_playlist_id}")
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return {"error": f"Failed to create YouTube Music playlist: {str(e)}"}
        
        # Transfer tracks
        transferred_count = 0
        failed_tracks = []
        video_ids = []
        
        for i, track in enumerate(tracks):
            if track['track']:
                track_name = track['track']['name']
                artists = [artist['name'] for artist in track['track']['artists']]
                search_query = f"{track_name} {' '.join(artists)}"
                
                print(f"Processing track {i+1}/{len(tracks)}: {track_name} by {', '.join(artists)}")
                
                # Search for the song on YouTube Music
                try:
                    video_id = search_youtube_music(ytm, search_query)
                    
                    if video_id:
                        video_ids.append(video_id)
                        transferred_count += 1
                        print(f"✓ Found: {video_id}")
                    else:
                        failed_tracks.append({
                            'name': track_name,
                            'artists': artists
                        })
                        print(f"✗ Not found")
                except Exception as e:
                    print(f"Error searching for track: {e}")
                    failed_tracks.append({
                        'name': track_name,
                        'artists': artists
                    })
        
        # Add all found songs to the playlist
        if video_ids:
            try:
                ytm.add_playlist_items(ytm_playlist_id, video_ids)
                print(f"Added {len(video_ids)} tracks to playlist")
            except Exception as e:
                print(f"Error adding tracks to playlist: {e}")
                return {"error": f"Failed to add tracks to playlist: {str(e)}"}
        
        print(f"Transfer completed. {transferred_count} tracks transferred, {len(failed_tracks)} failed")
        
        return {
            "success": True,
            "playlist_name": playlist_name,
            "total_tracks": len(tracks),
            "transferred_count": transferred_count,
            "failed_tracks": failed_tracks,
            "ytm_playlist_id": ytm_playlist_id
        }
        
    except Exception as e:
        print(f"Unexpected error in transfer_playlist: {e}")
        return {"error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Simple HTML for testing
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>NeverPay2Spotify - Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f23; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #333; border-radius: 5px; background: #1a1a2e; color: white; }
        button { padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
        .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; }
        .error { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 NeverPay2Spotify - Debug Version</h1>
        <p>Test your YouTube Music headers and transfer playlists!</p>
        
        <div class="form-group">
            <label for="spotifyUrl">Spotify Playlist URL:</label>
            <input type="url" id="spotifyUrl" placeholder="https://open.spotify.com/playlist/...">
        </div>
        
        <div class="form-group">
            <label for="ytmusicHeaders">YouTube Music Headers (JSON):</label>
            <textarea id="ytmusicHeaders" rows="10" placeholder='{"Cookie": "...", "Authorization": "...", ...}'></textarea>
        </div>
        
        <button onclick="testHeaders()">Test Headers</button>
        <button onclick="transferPlaylist()">Transfer Playlist</button>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        async function testHeaders() {
            const headers = document.getElementById('ytmusicHeaders').value;
            let parsedHeaders;
            try {
                parsedHeaders = JSON.parse(headers);
            } catch (e) {
                showResult('Invalid JSON format!', 'error');
                return;
            }
            
            try {
                const response = await fetch('/test-headers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ytmusic_headers: parsedHeaders })
                });
                const result = await response.json();
                
                if (result.error) {
                    showResult('Header Test Failed: ' + result.error, 'error');
                } else {
                    showResult('Header Test Successful! User: ' + JSON.stringify(result.user_info), 'success');
                }
            } catch (error) {
                showResult('Network Error: ' + error.message, 'error');
            }
        }
        
        async function transferPlaylist() {
            const url = document.getElementById('spotifyUrl').value;
            const headers = document.getElementById('ytmusicHeaders').value;
            
            if (!url || !headers) {
                showResult('Please fill in both fields!', 'error');
                return;
            }
            
            let parsedHeaders;
            try {
                parsedHeaders = JSON.parse(headers);
            } catch (e) {
                showResult('Invalid JSON format!', 'error');
                return;
            }
            
            try {
                const response = await fetch('/transfer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        spotify_url: url,
                        ytmusic_headers: parsedHeaders
                    })
                });
                const result = await response.json();
                
                if (result.error) {
                    showResult('Transfer Failed: ' + result.error, 'error');
                } else {
                    showResult('Transfer Successful! ' + result.transferred_count + ' tracks transferred. Playlist ID: ' + result.ytm_playlist_id, 'success');
                }
            } catch (error) {
                showResult('Network Error: ' + error.message, 'error');
            }
        }
        
        function showResult(message, type) {
            const result = document.getElementById('result');
            result.textContent = message;
            result.className = 'result ' + type;
            result.style.display = 'block';
        }
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode('utf-8'))

    def do_POST(self):
        if self.path == '/transfer':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                spotify_url = data.get('spotify_url')
                ytmusic_headers = data.get('ytmusic_headers')
                
                if not spotify_url or not ytmusic_headers:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing required parameters"}).encode('utf-8'))
                    return
                
                # First test the YouTube Music headers
                test_result = test_youtube_music_headers(ytmusic_headers)
                if not test_result.get('success'):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": f"YouTube Music authentication failed: {test_result.get('error')}",
                        "debug_info": "Please check your headers. Make sure you're logged into YouTube Music and the headers are fresh."
                    }).encode('utf-8'))
                    return
                
                # Perform the actual transfer
                result = transfer_playlist(spotify_url, ytmusic_headers)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif self.path == '/test-headers':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                ytmusic_headers = data.get('ytmusic_headers')
                
                if not ytmusic_headers:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing YouTube Music headers"}).encode('utf-8'))
                    return
                
                # Test the headers
                result = test_youtube_music_headers(ytmusic_headers)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
