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

def transfer_playlist(spotify_playlist_url, ytmusic_headers, spotify_client_id=None, spotify_client_secret=None):
    """Transfer a Spotify playlist to YouTube Music"""
    try:
        # Initialize YouTube Music with provided headers
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
    """Get the HTML template content with modern 21st.dev inspired design"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeverPay2Spotify - Transfer Playlists</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #818cf8;
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
            --background: #0f0f23;
            --surface: #1a1a2e;
            --surface-light: #16213e;
            --text: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border: #334155;
            --border-light: #475569;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
            --shadow-xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
            --gradient: linear-gradient(135deg, var(--primary), var(--primary-dark));
            --gradient-hover: linear-gradient(135deg, var(--primary-light), var(--primary));
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--background);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .header {
            text-align: center;
            margin-bottom: 4rem;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50px;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 200px;
            background: var(--gradient);
            filter: blur(100px);
            opacity: 0.3;
            z-index: -1;
        }

        .header h1 {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            letter-spacing: -0.02em;
        }

        .header p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
            font-weight: 400;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: start;
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 1.5rem;
            padding: 2.5rem;
            box-shadow: var(--shadow-xl);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 30px 60px -12px rgb(0 0 0 / 0.4);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text);
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border);
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: all 0.2s;
            background: var(--surface-light);
            color: var(--text);
        }

        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1);
            background: var(--surface);
        }

        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: var(--text-muted);
        }

        .btn {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: var(--shadow);
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: var(--gradient-hover);
            transition: left 0.3s ease;
        }

        .btn:hover::before {
            left: 0;
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

        .btn span {
            position: relative;
            z-index: 1;
        }

        .notification {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: none;
            border: 1px solid;
            font-weight: 500;
        }

        .notification.success {
            background: rgb(16 185 129 / 0.1);
            border-color: var(--success);
            color: var(--success);
        }

        .notification.error {
            background: rgb(239 68 68 / 0.1);
            border-color: var(--error);
            color: var(--error);
        }

        .notification.warning {
            background: rgb(245 158 11 / 0.1);
            border-color: var(--warning);
            color: var(--warning);
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
            border: 1px solid;
        }

        .result.success {
            background: rgb(16 185 129 / 0.05);
            border-color: var(--success);
        }

        .result.error {
            background: rgb(239 68 68 / 0.05);
            border-color: var(--error);
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .optional-note {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
            font-style: italic;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .stat-card {
            background: var(--surface-light);
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid var(--border);
            text-align: center;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .failed-tracks {
            margin-top: 1.5rem;
            padding: 1.5rem;
            background: var(--surface-light);
            border-radius: 0.75rem;
            border: 1px solid var(--border);
        }

        .failed-tracks h4 {
            color: var(--warning);
            margin-bottom: 1rem;
        }

        .track-item {
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .track-item:last-child {
            border-bottom: none;
        }

        .track-info {
            flex: 1;
        }

        .track-name {
            font-weight: 600;
            color: var(--text);
        }

        .track-artists {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .demo-section {
            background: var(--surface-light);
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 2rem;
            margin-top: 2rem;
        }

        .demo-section h3 {
            color: var(--primary);
            margin-bottom: 1rem;
        }

        .demo-section p {
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .demo-button {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .demo-button:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow);
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .card {
                padding: 1.5rem;
            }
        }

        .floating-elements {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }

        .floating-element {
            position: absolute;
            background: var(--gradient);
            border-radius: 50%;
            opacity: 0.1;
            animation: float 20s infinite linear;
        }

        .floating-element:nth-child(1) {
            width: 100px;
            height: 100px;
            top: 10%;
            left: 10%;
            animation-delay: 0s;
        }

        .floating-element:nth-child(2) {
            width: 150px;
            height: 150px;
            top: 60%;
            right: 10%;
            animation-delay: -5s;
        }

        .floating-element:nth-child(3) {
            width: 80px;
            height: 80px;
            bottom: 20%;
            left: 20%;
            animation-delay: -10s;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(120deg); }
            66% { transform: translateY(20px) rotate(240deg); }
        }
    </style>
</head>
<body>
    <div class="floating-elements">
        <div class="floating-element"></div>
        <div class="floating-element"></div>
        <div class="floating-element"></div>
    </div>

    <div class="container">
        <div class="header">
            <h1>🎵 NeverPay2Spotify</h1>
            <p>Say goodbye to Spotify's subscription fees and hello to YouTube Music's... well, also subscription fees, but at least you get video! 🎬</p>
        </div>

        <div class="main-content">
            <div class="card">
                <div class="notification" id="notification"></div>

                <form id="transferForm">
                    <div class="section-title">
                        <span>🚀</span>
                        The Great Migration Guide
                    </div>
                    
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
                    
                    <button type="submit" class="btn" id="submitBtn">
                        <span>Launch The Great Migration! 🚀</span>
                    </button>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Your music is packing its bags and moving to YouTube Music... This may take a few minutes. 🎵✈️</p>
                </div>

                <div class="result" id="result"></div>
            </div>

            <div class="card">
                <div class="section-title">
                    <span>📋</span>
                    Quick Setup Guide
                </div>
                
                <div class="demo-section">
                    <h3>🎯 Try with Demo Data</h3>
                    <p>Want to see how it works? Click the button below to load the Linkin Park playlist and YouTube Music headers!</p>
                    <button class="demo-button" onclick="loadDemoData()">Load Demo Data</button>
                </div>

                <div class="demo-section">
                    <h3>🔧 How to Get YouTube Music Headers</h3>
                    <ol style="color: var(--text-secondary); line-height: 1.8;">
                        <li>Open YouTube Music in your browser</li>
                        <li>Press F12 to open Developer Tools</li>
                        <li>Go to Network tab</li>
                        <li>Refresh the page or perform any action</li>
                        <li>Click on any request to music.youtube.com</li>
                        <li>Copy the request headers (Cookie, Authorization, etc.)</li>
                        <li>Paste them as JSON in the form</li>
                    </ol>
                </div>

                <div class="demo-section">
                    <h3>🎵 Supported Playlists</h3>
                    <p style="color: var(--text-secondary);">Any public Spotify playlist can be transferred! The app will:</p>
                    <ul style="color: var(--text-secondary); line-height: 1.8; margin-top: 0.5rem;">
                        <li>Extract all songs from your Spotify playlist</li>
                        <li>Search for each song on YouTube Music</li>
                        <li>Create a new private playlist on YouTube Music</li>
                        <li>Add all found songs to the new playlist</li>
                        <li>Show you which songs couldn't be found</li>
                    </ul>
                </div>
            </div>
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

        function loadDemoData() {
            const demoHeaders = {
                "Cookie": "VISITOR_INFO1_LIVE=md7hWI_1LWU; VISITOR_PRIVACY_METADATA=CgJCRBIEGgAgGw%3D%3D; PREF=f4=4000000&f6=40000000&tz=Asia.Dhaka&f7=100; SID=g.a0000AjQvaw589NDKMP2agwI4J4eKgkstv1AcukzMJvXgTgO7aJtbNK2BY03CJyySuj7EOPZSAACgYKAUcSARASFQHGX2MiG0csl0tFTlYRVAvAJh21IxoVAUF8yKpeum9LV7sRJfP1z-iXcetI0076; __Secure-1PSID=g.a0000AjQvaw589NDKMP2agwI4J4eKgkstv1AcukzMJvXgTgO7aJtD-PS8EKWX30e3bBqBlZZgAACgYKASYSARASFQHGX2Migpnnanc8YnYdny1-cMVCKBoVAUF8yKq_1aQngkrja98av14JoLtv0076; __Secure-3PSID=g.a0000AjQvaw589NDKMP2agwI4J4eKgkstv1AcukzMJvXgTgO7aJtzZUXNCTxWYyFajcg2Oer4gACgYKAYoSARASFQHGX2MiXWL-8aMNmyMD-Z0k2h1sbxoVAUF8yKp7RZk0Cc4OPxABKWn2mvxd0076; HSID=Ag2W3CKNptVAFbo6Y; SSID=Ann5hMZfqIWNlrCTC; APISID=s8hzobBfGzkH9Apd/AaPtMHxQsgYPWvK0E; SAPISID=BODVw617_cm0JjAs/AjkzlwweiJ-EeaASZ; __Secure-1PAPISID=BODVw617_cm0JjAs/AjkzlwweiJ-EeaASZ; __Secure-3PAPISID=BODVw617_cm0JjAs/AjkzlwweiJ-EeaASZ; YSC=e_8pnqipNEA; __Secure-ROLLOUT_TOKEN=CKP928OH-_eM1QEQxbPK3eDrjgMYu6jOpqyMjwM%3D; __Secure-1PSIDTS=sidts-CjIB5H03PwzxFR0nxVsE_V1QIe1kWtInd3yHgzF-8DWqPyNcpIL1IcNhDbHhJZtaNccz8hAA; __Secure-3PSIDTS=sidts-CjIB5H03PwzxFR0nxVsE_V1QIe1kWtInd3yHgzF-8DWqPyNcpIL1IcNhDbHhJZtaNccz8hAA; LOGIN_INFO=AFmmF2swRgIhAKnwqWDrPGCA0UsBkoeowUZacULrBOq5oBGT5KSjejzkAiEAiYyVESuXAtFNziZXqSYKG8MGU_Lizj7Hi7_I5EazJfw:QUQ3MjNmd1VXVkR5QnRPMXZ4Yi1BdWhlSWlBSDhVVi1KbVhWWWhCMl9nb05penhKUk41XzVIMTktUl9jNFRIZVA2WVRXY0FEWmZZQTc3T0tVNWpoMTU4QzV2RkRDdm0yamZBQ002OGNSbDdlNDM3MTlaX3p1cXBhbGQ0NFpDUllES29SUnRqLVFaeE5SbjNKV0tvTFdnTDBsTkFlTGNZX3dB; CONSISTENCY=AKreu9tHdbzAFuQ31GhTVEV-qEfqyDP749xxQKhOyQlmuwIBC8r2yOfdtUtxJmRPlY_BCvcys6QsorRtvbJuc_bhY4DF9sJWldWAtvXKccisbx8U2CClIqrPpXK-TomqMKoxCKaqjIedzGzR4NUhEjqJ; SIDCC=AKEyXzXB69i7WMp-HdY801IhJK5IHN4jjHO0onEGNzbLfqh1sHkL7hw-90pnsdv8I-cRImiE950; __Secure-1PSIDCC=AKEyXzVDOs8GAPRajEbLKm-hKp8SIhE8qpR3UBYqo_cJPpbf9OoTo687rUxhDy6GdWTV26TFI_A; __Secure-3PSIDCC=AKEyXzWCV_LujMjz5wDtjye1S0zho3SCNx_C5JRnCRM-SYpaj1v5L3o3-K-BjElYejGrdL-kTg",
                "Authorization": "SAPISIDHASH 1755245138_c2faf26b16b518ad5ba563c2caa0fc142c253d78_u SAPISID1PHASH 1755245138_c2faf26b16b518ad5ba563c2caa0fc142c253d78_u SAPISID3PHASH 1755245138_c2faf26b16b518ad5ba563c2caa0fc142c253d78_u",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "Origin": "https://music.youtube.com",
                "Referer": "https://music.youtube.com/",
                "Sec-Ch-Ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "same-origin",
                "Sec-Fetch-Site": "same-origin"
            };
            
            document.getElementById('spotifyUrl').value = 'https://open.spotify.com/playlist/4dnxoZHyjg7A31vH1pIZXR?si=eed04475eb00418b';
            document.getElementById('ytmusicHeaders').value = JSON.stringify(demoHeaders, null, 2);
            showNotification('Demo data loaded! Ready to test the Linkin Park playlist transfer! 🎸', 'success');
        }

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const spotifyUrl = document.getElementById('spotifyUrl').value;
            const ytmusicHeadersText = document.getElementById('ytmusicHeaders').value;

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
                        ytmusic_headers: ytmusicHeaders
                    })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showResult(`<strong>Migration Failed 😅</strong><br><br>Error: ${result.error}`, 'error');
                } else {
                    const statsHtml = `
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${result.total_tracks}</div>
                                <div class="stat-label">Total Tracks</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${result.transferred_count}</div>
                                <div class="stat-label">Transferred</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${result.failed_tracks.length}</div>
                                <div class="stat-label">Failed</div>
                            </div>
                        </div>
                    `;

                    const failedTracksHtml = result.failed_tracks.length > 0 ? `
                        <div class="failed-tracks">
                            <h4>🎵 Failed to Transfer (${result.failed_tracks.length} tracks)</h4>
                            ${result.failed_tracks.slice(0, 10).map(track => `
                                <div class="track-item">
                                    <div class="track-info">
                                        <div class="track-name">${track.name}</div>
                                        <div class="track-artists">${track.artists.join(', ')}</div>
                                    </div>
                                </div>
                            `).join('')}
                            ${result.failed_tracks.length > 10 ? `<p style="color: var(--text-muted); margin-top: 1rem;">... and ${result.failed_tracks.length - 10} more tracks</p>` : ''}
                        </div>
                    ` : '';

                    showResult(`
                        <strong>Migration Successful! 🎉</strong><br><br>
                        <h3 style="color: var(--primary); margin-bottom: 1rem;">${result.playlist_name}</h3>
                        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">YouTube Music Playlist ID: <code style="background: var(--surface-light); padding: 0.25rem 0.5rem; border-radius: 0.25rem;">${result.ytm_playlist_id}</code></p>
                        ${statsHtml}
                        ${failedTracksHtml}
                    `, 'success');
                }
            } catch (error) {
                showResult(`<strong>Network Error 😱</strong><br><br>Error: ${error.message}`, 'error');
            } finally {
                hideLoading();
            }
        });
    </script>
</body>
</html>
    """

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(get_html_template().encode('utf-8'))
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
