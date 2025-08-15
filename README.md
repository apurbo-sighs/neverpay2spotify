# NeverPay2Spotify 🎵

A modern, beautiful web application to transfer your Spotify playlists to YouTube Music - **Because who needs another subscription fee, right?** 😅

![NeverPay2Spotify](https://img.shields.io/badge/Status-Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-lightgrey)

## ✨ Features

- 🎨 **Modern UI/UX** - Beautiful, responsive design inspired by 21st.dev components (because looks matter!)
- 🔄 **Seamless Transfer** - Transfer entire Spotify playlists to YouTube Music (like moving house, but for music)
- 📊 **Real-time Progress** - See transfer progress and statistics (watch your music pack its bags)
- 🔐 **Secure** - Your credentials stay local, never sent to external servers (your secrets are safe with us)
- 🚀 **Fast & Efficient** - Optimized search and transfer algorithms (faster than a caffeinated developer)
- 📱 **Mobile Friendly** - Works perfectly on all devices (even your grandma's flip phone)
- 🎯 **High Success Rate** - Smart song matching for better results (we're like a music detective)

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher (because we're not savages using Python 2)
- A Spotify account with playlists (the ones you're breaking up with)
- A YouTube Music account (your music's new home)
- YouTube Music headers (see setup below - think of it as your music's visa)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd neverpay2spotify
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get YouTube Music Headers (Your Music's Passport)**
   
   First, install ytmusicapi globally:
   ```bash
   pip install ytmusicapi
   ```
   
   Then run the setup command:
   ```bash
   ytmusicapi setup
   ```
   
   This will guide you through getting your YouTube Music headers. Think of it as applying for your music's visa to enter YouTube Music. Save the generated JSON file.

4. **Run the application**
   ```bash
   python neverpay2spotify.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📋 How to Use (The Great Migration Guide)

### Step 1: Get YouTube Music Headers (The Visa Application)
1. Run `ytmusicapi setup` in your terminal
2. Follow the instructions to extract headers from your browser (like filling out immigration forms)
3. Save the generated JSON file (your music's golden ticket)

### Step 2: Transfer Your Playlist (The Journey Begins)
1. **Upload Headers**: Upload your YouTube Music headers JSON file (show your passport)
2. **Enter Spotify URL**: Paste your Spotify playlist URL (the address of your musical homeland)
3. **Optional**: Add Spotify API credentials for better performance (VIP access)
4. **Transfer**: Click the transfer button and wait for completion (your music's flight to freedom)

### Step 3: Enjoy Your Music (Welcome to Your New Home!)
- Your playlist will be created in YouTube Music (unpack those bags!)
- Check the transfer statistics (see how many songs made it through customs)
- Review any failed tracks (the ones that got lost in transit)

## 🔧 Advanced Setup

### Spotify API Credentials (The VIP Pass - Optional)

For better performance and higher rate limits (like having backstage access):

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application (apply for your VIP pass)
3. Copy your Client ID and Client Secret (your backstage credentials)
4. Enter them in the web interface (show your VIP pass at the door)

### Environment Variables

You can also set Spotify credentials as environment variables:

```bash
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"
```

## 🎨 Features Breakdown

### Modern Design
- **21st.dev Inspired**: Modern card-based layout with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Interactive**: Hover effects, loading states, and smooth transitions
- **Accessible**: Proper contrast ratios and keyboard navigation

### Smart Transfer
- **Intelligent Matching**: Advanced search algorithms for better song matching
- **Batch Processing**: Efficient handling of large playlists
- **Error Handling**: Graceful handling of failed transfers
- **Progress Tracking**: Real-time feedback during transfer

### Security & Privacy
- **Local Processing**: All data stays on your device
- **No External Servers**: Your credentials never leave your machine
- **Secure Headers**: YouTube Music authentication handled locally

## 📊 Transfer Statistics

The application provides detailed statistics for each transfer:

- **Total Tracks**: Number of songs in the original playlist
- **Successfully Transferred**: Songs that were found and added
- **Success Rate**: Percentage of successful transfers
- **Failed Tracks**: List of songs that couldn't be transferred
- **Playlist ID**: YouTube Music playlist identifier

## 🛠️ Troubleshooting

### Common Issues

**"Invalid YouTube Music headers"**
- Make sure you're using the latest headers from `ytmusicapi setup`
- Headers expire periodically, regenerate them if needed

**"Spotify playlist not found"**
- Verify the playlist URL is correct and public
- Ensure you have access to the playlist

**"Transfer failed"**
- Check your internet connection
- Verify YouTube Music headers are valid
- Try with a smaller playlist first

**"Low success rate"**
- Some songs may not be available on YouTube Music
- Try adding Spotify API credentials for better search results
- Check the failed tracks list for specific issues

### Getting Help

1. Check the console output for detailed error messages
2. Verify all prerequisites are met
3. Try with a simple, small playlist first
4. Ensure your YouTube Music headers are fresh

## 🔒 Privacy & Security

- **No Data Collection**: This application doesn't collect or store any personal data
- **Local Processing**: All transfers happen on your local machine
- **Open Source**: Full transparency of the codebase
- **No External Dependencies**: Minimal external API calls

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API wrapper
- [spotipy](https://github.com/spotipy-dev/spotipy) - Spotify Web API wrapper
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [21st.dev](https://21st.dev) - Design inspiration

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the console output for error messages
3. Try with a different playlist
4. Ensure all dependencies are up to date

---

**Made with ❤️ for music lovers who want to break free from subscription services! Because life is too short to pay for the same music twice! 🎵💸**
