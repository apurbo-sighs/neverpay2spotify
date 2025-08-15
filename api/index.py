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
    """Get the HTML template content with simplified design"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeverPay2Spotify - Transfer Playlists</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #000000;
            color: #ffffff;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .container {
            max-width: 600px;
            width: 100%;
        }

        .tabs {
            display: flex;
            margin-bottom: 2rem;
            background: #111111;
            border-radius: 12px;
            padding: 4px;
        }

        .tab {
            flex: 1;
            padding: 12px 24px;
            text-align: center;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            color: #888888;
        }

        .tab.active {
            background: #1a1a1a;
            color: #ffffff;
        }

        .form-group {
            margin-bottom: 2rem;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #ffffff;
            font-size: 1rem;
        }

        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 1rem;
            border: 1px solid #333333;
            border-radius: 8px;
            font-size: 1rem;
            background: #111111;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #ffffff;
        }

        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: #666666;
        }

        .headers-help {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .help-text {
            color: #888888;
            font-size: 0.9rem;
        }

        .help-buttons {
            display: flex;
            gap: 0.5rem;
        }

        .help-btn {
            padding: 6px 12px;
            border: none;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.3s ease;
        }

        .help-btn.video {
            background: #dc2626;
            color: white;
        }

        .help-btn.steps {
            background: #2563eb;
            color: white;
        }

        .help-btn:hover {
            transform: translateY(-1px);
            opacity: 0.9;
        }

        .transfer-btn {
            width: 100%;
            background: #dc2626;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }

        .transfer-btn:hover {
            background: #b91c1c;
            transform: translateY(-2px);
        }

        .transfer-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .youtube-icon {
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .youtube-icon::before {
            content: '';
            width: 0;
            height: 0;
            border-left: 6px solid #dc2626;
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            margin-left: 2px;
        }

        .notification {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: none;
            font-weight: 500;
        }

        .notification.success {
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid #22c55e;
            color: #22c55e;
        }

        .notification.error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            color: #ef4444;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }

        .spinner {
            border: 3px solid #333333;
            border-top: 3px solid #dc2626;
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
            border-radius: 8px;
            display: none;
            border: 1px solid;
        }

        .result.success {
            background: rgba(34, 197, 94, 0.05);
            border-color: #22c55e;
        }

        .result.error {
            background: rgba(239, 68, 68, 0.05);
            border-color: #ef4444;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 1rem 0;
        }

        .stat {
            text-align: center;
            padding: 1rem;
            background: #111111;
            border-radius: 8px;
        }

        .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #dc2626;
        }

        .stat-label {
            font-size: 0.8rem;
            color: #888888;
            margin-top: 0.25rem;
        }

        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .container {
                max-width: 100%;
            }
            
            .help-buttons {
                flex-direction: column;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="tabs">
            <div class="tab active">Browser Headers</div>
            <div class="tab">Premium</div>
        </div>

        <div class="notification" id="notification"></div>

        <form id="transferForm">
            <div class="form-group">
                <label for="spotifyUrl">Spotify Playlist URL</label>
                <input type="url" id="spotifyUrl" required placeholder="https://open.spotify.com/playlist/...">
            </div>
            
            <div class="form-group">
                <label for="ytmusicHeaders">YouTube Music Headers</label>
                <div class="headers-help">
                    <span class="help-text">How to get headers?</span>
                    <div class="help-buttons">
                        <button type="button" class="help-btn video" onclick="showVideoHelp()">
                            ▶ Watch video
                        </button>
                        <button type="button" class="help-btn steps" onclick="showStepsHelp()">
                            ⤢ Step-by-step
                        </button>
                    </div>
                </div>
                <textarea id="ytmusicHeaders" rows="8" required placeholder="Paste your YouTube Music headers here..."></textarea>
            </div>
            
            <button type="submit" class="transfer-btn" id="submitBtn">
                <div class="youtube-icon"></div>
                Transfer to YouTube Music
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Transferring your playlist... This may take a few minutes.</p>
        </div>

        <div class="result" id="result"></div>
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

        function showVideoHelp() {
            showNotification('Video tutorial coming soon! For now, use the step-by-step guide.', 'error');
        }

        function showStepsHelp() {
            const steps = `
                <strong>How to get YouTube Music headers:</strong><br><br>
                1. Open YouTube Music in your browser<br>
                2. Press F12 to open Developer Tools<br>
                3. Go to Network tab<br>
                4. Refresh the page or perform any action<br>
                5. Click on any request to music.youtube.com<br>
                6. Copy the request headers (Cookie, Authorization, etc.)<br>
                7. Paste them as JSON in the form above
            `;
            showNotification(steps, 'success');
        }

        // Load demo data when page loads
        window.addEventListener('load', function() {
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
        });

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const spotifyUrl = document.getElementById('spotifyUrl').value;
            const ytmusicHeadersText = document.getElementById('ytmusicHeaders').value;

            // Validate headers JSON
            let ytmusicHeaders;
            try {
                ytmusicHeaders = JSON.parse(ytmusicHeadersText);
            } catch (error) {
                showNotification('Invalid JSON in YouTube Music headers. Please check your format!', 'error');
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
                    showResult(`<strong>Transfer Failed</strong><br><br>Error: ${result.error}`, 'error');
                } else {
                    const statsHtml = `
                        <div class="stats">
                            <div class="stat">
                                <div class="stat-number">${result.total_tracks}</div>
                                <div class="stat-label">Total Tracks</div>
                            </div>
                            <div class="stat">
                                <div class="stat-number">${result.transferred_count}</div>
                                <div class="stat-label">Transferred</div>
                            </div>
                            <div class="stat">
                                <div class="stat-number">${result.failed_tracks.length}</div>
                                <div class="stat-label">Failed</div>
                            </div>
                        </div>
                    `;

                    showResult(`
                        <strong>Transfer Successful! 🎉</strong><br><br>
                        <strong>Playlist:</strong> ${result.playlist_name}<br>
                        <strong>YouTube Music Playlist ID:</strong> ${result.ytm_playlist_id}<br><br>
                        ${statsHtml}
                        ${result.failed_tracks.length > 0 ? `<br><strong>Failed tracks:</strong> ${result.failed_tracks.length} songs couldn't be found on YouTube Music.` : ''}
                    `, 'success');
                }
            } catch (error) {
                showResult(`<strong>Network Error</strong><br><br>Error: ${error.message}`, 'error');
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
