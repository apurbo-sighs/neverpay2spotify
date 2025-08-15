#!/usr/bin/env python3
"""
NeverPay2Spotify - Vercel Serverless Function
"""

import json
import re
from http.server import BaseHTTPRequestHandler

def extract_playlist_id_from_url(spotify_url):
    """Extract playlist ID from Spotify URL"""
    if 'spotify.com/playlist/' in spotify_url:
        match = re.search(r'playlist/([a-zA-Z0-9]+)', spotify_url)
        if match:
            return match.group(1)
    return None

def test_youtube_music_headers(ytmusic_headers):
    """Test if YouTube Music headers are valid"""
    try:
        # Basic validation - check if required headers exist
        required_headers = ['Cookie', 'Authorization']
        missing_headers = [h for h in required_headers if h not in ytmusic_headers]
        
        if missing_headers:
            return {"error": f"Missing required headers: {', '.join(missing_headers)}"}
        
        # Check if headers have content
        if not ytmusic_headers.get('Cookie') or not ytmusic_headers.get('Authorization'):
            return {"error": "Cookie and Authorization headers cannot be empty"}
        
        return {"success": True, "user_info": {"message": "Headers look valid"}}
    except Exception as e:
        return {"error": str(e)}

def transfer_playlist(spotify_playlist_url, ytmusic_headers):
    """Simulate transfer for testing"""
    try:
        print(f"Starting transfer for URL: {spotify_playlist_url}")
        print(f"Headers provided: {list(ytmusic_headers.keys())}")
        
        # Extract playlist ID from URL
        playlist_id = extract_playlist_id_from_url(spotify_playlist_url)
        if not playlist_id:
            return {"error": "Invalid Spotify playlist URL"}
        
        print(f"Extracted playlist ID: {playlist_id}")
        
        # For now, just return success to test the flow
        return {
            "success": True,
            "playlist_name": "Test Playlist",
            "total_tracks": 5,
            "transferred_count": 3,
            "failed_tracks": [],
            "ytm_playlist_id": "test_playlist_id_123"
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
        <h1>🎵 NeverPay2Spotify - Test Version</h1>
        <p>Testing basic functionality first...</p>
        
        <div class="form-group">
            <label for="spotifyUrl">Spotify Playlist URL:</label>
            <input type="url" id="spotifyUrl" placeholder="https://open.spotify.com/playlist/...">
        </div>
        
        <div class="form-group">
            <label for="ytmusicHeaders">YouTube Music Headers (JSON):</label>
            <textarea id="ytmusicHeaders" rows="10" placeholder='{"Cookie": "...", "Authorization": "...", ...}'></textarea>
        </div>
        
        <button onclick="testHeaders()">Test Headers</button>
        <button onclick="transferPlaylist()">Test Transfer</button>
        
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
                    showResult('Header Test Successful! ' + JSON.stringify(result.user_info), 'success');
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
                    showResult('Transfer Test Successful! ' + result.transferred_count + ' tracks transferred. Playlist ID: ' + result.ytm_playlist_id, 'success');
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
                
                # Perform the transfer
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
