#!/usr/bin/env python3
"""
NeverPay2Spotify - Vercel Serverless Function
A serverless version of the Spotify to YouTube Music playlist transfer app.
"""

import json
import os
from http.server import BaseHTTPRequestHandler

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
                
                # For now, just return a demo response
                # In a real implementation, you would process the transfer here
                response_data = {
                    "success": True,
                    "playlist_name": "Demo Playlist",
                    "total_tracks": 10,
                    "transferred_count": 8,
                    "failed_tracks": [
                        {"name": "Song 1", "artists": ["Artist 1"]},
                        {"name": "Song 2", "artists": ["Artist 2"]}
                    ],
                    "ytm_playlist_id": "demo_playlist_id_123"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
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
