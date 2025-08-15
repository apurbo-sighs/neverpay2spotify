#!/usr/bin/env python3
"""
NeverPay2Spotify - Startup Script
A simple launcher for the NeverPay2Spotify application
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'ytmusicapi', 'spotipy', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'neverpay2spotify.py',
        'templates/index.html',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎵 NeverPay2Spotify - Transfer Playlists")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    print("✅ All dependencies found!")
    
    # Check files
    print("📁 Checking files...")
    if not check_files():
        input("\nPress Enter to exit...")
        sys.exit(1)
    print("✅ All files found!")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        uploads_dir.mkdir()
        print("📁 Created uploads directory")
    
    print("\n🚀 Starting NeverPay2Spotify...")
    print("📖 Make sure you have your YouTube Music headers ready!")
    print("🔗 The app will open in your browser automatically.")
    print("\n" + "=" * 50)
    
    # Import and run the Flask app
    try:
        from neverpay2spotify import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using NeverPay2Spotify!")
    except Exception as e:
        print(f"\n❌ Error starting the application: {e}")
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
