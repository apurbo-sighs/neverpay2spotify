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
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeverPay2Spotify - Transfer Playlists</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --success: #10b981;
            --error: #ef4444;
            --background: #f8fafc;
            --surface: #ffffff;
            --text: #1e293b;
            --text-secondary: #64748b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--background);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .header p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }

        .card {
            background: var(--surface);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text);
        }

        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border);
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: all 0.2s;
            background: var(--surface);
        }

        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1);
        }

        .upload-section {
            border: 2px dashed var(--border);
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
            transition: all 0.2s;
            cursor: pointer;
        }

        .upload-section:hover {
            border-color: var(--primary);
            background: rgb(99 102 241 / 0.05);
        }

        .upload-section.dragover {
            border-color: var(--primary);
            background: rgb(99 102 241 / 0.1);
        }

        .btn {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: var(--shadow);
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .notification {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: none;
        }

        .notification.success {
            background: rgb(16 185 129 / 0.1);
            border: 1px solid var(--success);
            color: var(--success);
        }

        .notification.error {
            background: rgb(239 68 68 / 0.1);
            border: 1px solid var(--error);
            color: var(--error);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }

        .spinner {
            border: 3px solid var(--border);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result {
            margin-top: 2rem;
            padding: 1.5rem;
            border-radius: 0.5rem;
            display: none;
        }

        .result.success {
            background: rgb(16 185 129 / 0.1);
            border: 1px solid var(--success);
        }

        .result.error {
            background: rgb(239 68 68 / 0.1);
            border: 1px solid var(--error);
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text);
        }

        .optional-note {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 NeverPay2Spotify</h1>
            <p>Say goodbye to Spotify's subscription fees and hello to YouTube Music's... well, also subscription fees, but at least you get video! 🎬</p>
        </div>

        <div class="card">
            <div class="notification" id="notification"></div>

            <form id="transferForm">
                <div class="section-title">The Great Migration Guide 📋</div>
                
                <div class="form-group">
                    <label for="spotifyUrl">The Playlist You're Breaking Up With 💔</label>
                    <input type="url" id="spotifyUrl" required placeholder="https://open.spotify.com/playlist/...">
                    <div class="optional-note">Paste your Spotify playlist URL here. Don't worry, it won't hurt... much.</div>
                </div>
                
                <div class="form-group">
                    <label for="ytmusicHeaders">Your YouTube Music Passport 🛂</label>
                    <textarea id="ytmusicHeaders" rows="8" required placeholder='{"Cookie": "your-cookie-here", "Authorization": "your-auth-here", ...}'></textarea>
                    <div class="optional-note">This is like your VIP pass to YouTube Music. Get it from your browser's developer tools!</div>
                </div>
                
                <div class="form-group">
                    <label for="spotifyClientId">Spotify API Credentials (The VIP Pass) 🎫</label>
                    <input type="text" id="spotifyClientId" placeholder="Your Spotify Client ID">
                    <div class="optional-note">Optional: Your Spotify API credentials. If you don't have them, we'll try to use the default ones.</div>
                </div>
                
                <div class="form-group">
                    <label for="spotifyClientSecret">The Secret Sauce 🔐</label>
                    <input type="password" id="spotifyClientSecret" placeholder="Your Spotify Client Secret">
                    <div class="optional-note">The secret part of your Spotify API credentials. Keep it safe!</div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">Launch The Great Migration! 🚀</button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Your music is packing its bags and moving to YouTube Music... This may take a few minutes. 🎵✈️</p>
            </div>

            <div class="result" id="result"></div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('transferForm');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const notification = document.getElementById('notification');
        const submitBtn = document.getElementById('submitBtn');

        function showNotification(message, type = 'success') {
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        }

        function showLoading() {
            form.style.display = 'none';
            loading.style.display = 'block';
            result.style.display = 'none';
            submitBtn.disabled = true;
        }

        function hideLoading() {
            form.style.display = 'block';
            loading.style.display = 'none';
            submitBtn.disabled = false;
        }

        function showResult(content, type = 'success') {
            result.innerHTML = content;
            result.className = `result ${type}`;
            result.style.display = 'block';
        }

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const spotifyUrl = document.getElementById('spotifyUrl').value;
            const ytmusicHeadersText = document.getElementById('ytmusicHeaders').value;
            const spotifyClientId = document.getElementById('spotifyClientId').value;
            const spotifyClientSecret = document.getElementById('spotifyClientSecret').value;

            // Validate headers JSON
            let ytmusicHeaders;
            try {
                ytmusicHeaders = JSON.parse(ytmusicHeadersText);
            } catch (error) {
                showNotification('Invalid JSON in YouTube Music headers. Please check your format! 😅', 'error');
                return;
            }

            showLoading();
            
            try {
                const response = await fetch('/transfer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        spotify_url: spotifyUrl,
                        ytmusic_headers: ytmusicHeaders,
                        spotify_client_id: spotifyClientId || null,
                        spotify_client_secret: spotifyClientSecret || null
                    })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showResult(`<strong>Migration Failed 😅</strong><br><br>Error: ${result.error}`, 'error');
                } else {
                    showResult(`
                        <strong>Migration Successful! 🎉</strong><br><br>
                        <strong>Playlist:</strong> ${result.playlist_name}<br>
                        <strong>Total tracks:</strong> ${result.total_tracks}<br>
                        <strong>Successfully transferred:</strong> ${result.transferred_count}<br>
                        <strong>YouTube Music Playlist ID:</strong> ${result.ytm_playlist_id}<br><br>
                        ${result.failed_tracks.length > 0 ? `<strong>Failed tracks (${result.failed_tracks.length}):</strong><br>` + 
                        result.failed_tracks.slice(0, 5).map(track => `• ${track.name} by ${track.artists.join(', ')}`).join('<br>') + 
                        (result.failed_tracks.length > 5 ? '<br>... and more' : '') : ''}
                    `, 'success');
                }
            } catch (error) {
                showResult(`<strong>Network Error 😱</strong><br><br>Error: ${error.message}`, 'error');
            } finally {
                hideLoading();
            }
        });

        // Handle file upload for headers
        const headersTextarea = document.getElementById('ytmusicHeaders');
        
        // Add drag and drop functionality
        headersTextarea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.parentElement.classList.add('dragover');
        });

        headersTextarea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.parentElement.classList.remove('dragover');
        });

        headersTextarea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.parentElement.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/json') {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        headersTextarea.value = e.target.result;
                        showNotification('Headers file uploaded successfully! 📁', 'success');
                    };
                    reader.readAsText(file);
                } else {
                    showNotification('Please upload a JSON file! 📄', 'error');
                }
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
