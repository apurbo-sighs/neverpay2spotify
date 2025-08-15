# 🚀 Deploy NeverPay2Spotify to Vercel

This guide will help you deploy the NeverPay2Spotify application to Vercel as a serverless function.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For version control
3. **Python Knowledge**: Basic understanding of Python and serverless functions

## 🔧 Setup Steps

### Step 1: Prepare Your Repository

1. **Fork or Clone** this repository to your GitHub account
2. **Ensure** you have the following files in your repository:
   - `api/index.py` - Main serverless function
   - `api/requirements.txt` - Python dependencies
   - `vercel.json` - Vercel configuration
   - `templates/index.html` - HTML template (optional, fallback included)

### Step 2: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)
2. **Click "New Project"**
3. **Import Git Repository**: Select your GitHub repository
4. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
5. **Click "Deploy"**

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Confirm deployment settings
   - Wait for deployment to complete

### Step 3: Configure Environment Variables (Optional)

For better Spotify API performance, you can set environment variables:

1. **Go to your Vercel project dashboard**
2. **Navigate to Settings → Environment Variables**
3. **Add the following variables**:
   - `SPOTIPY_CLIENT_ID`: Your Spotify Client ID
   - `SPOTIPY_CLIENT_SECRET`: Your Spotify Client Secret

## 🎯 How to Use the Deployed App

### 1. Get YouTube Music Headers

First, you need to get your YouTube Music headers:

```bash
# Install ytmusicapi globally
pip install ytmusicapi

# Run the setup command
ytmusicapi setup
```

This will guide you through extracting headers from your browser. Save the generated JSON file.

### 2. Use the Web Interface

1. **Visit your deployed URL** (e.g., `https://your-app.vercel.app`)
2. **Enter your Spotify playlist URL**
3. **Paste your YouTube Music headers** (JSON format)
4. **Optionally add Spotify API credentials** for better performance
5. **Click "Transfer Playlist"**

## 🔧 Configuration Details

### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "/api/index.py"
    },
    {
      "src": "/transfer",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 300
    }
  }
}
```

### Serverless Function Structure

The main function is in `api/index.py` and includes:

- **HTML Template**: Served at the root path (`/`)
- **Transfer Endpoint**: Handles playlist transfers (`/transfer`)
- **CORS Support**: Allows cross-origin requests
- **Error Handling**: Comprehensive error handling and responses

## 🚨 Important Notes

### Limitations

1. **Function Timeout**: Vercel functions have a 10-second timeout by default (extended to 300 seconds in config)
2. **Memory Limits**: Functions have memory constraints
3. **Cold Starts**: First request may be slower

### Best Practices

1. **Test Locally**: Test your function before deploying
2. **Monitor Usage**: Keep an eye on Vercel usage limits
3. **Update Headers**: YouTube Music headers expire, users need to refresh them periodically

### Troubleshooting

#### Common Issues

1. **"Function timeout"**
   - Large playlists may take longer than expected
   - Consider breaking into smaller playlists

2. **"Module not found"**
   - Ensure all dependencies are in `api/requirements.txt`
   - Check that `vercel.json` points to the correct file

3. **"Invalid headers"**
   - YouTube Music headers expire periodically
   - Users need to regenerate them using `ytmusicapi setup`

#### Debugging

1. **Check Vercel Logs**: Go to your project dashboard → Functions → View logs
2. **Test Locally**: Use `vercel dev` to test locally
3. **Check Dependencies**: Ensure all required packages are installed

## 🔄 Updates and Maintenance

### Updating the Deployment

1. **Push changes** to your GitHub repository
2. **Vercel will automatically redeploy** (if auto-deploy is enabled)
3. **Or manually redeploy** from the Vercel dashboard

### Monitoring

- **Function Logs**: Check Vercel dashboard for function logs
- **Performance**: Monitor function execution times
- **Errors**: Set up error tracking if needed

## 🎉 Success!

Once deployed, your NeverPay2Spotify app will be available at your Vercel URL. Users can transfer their Spotify playlists to YouTube Music directly from the web interface!

## 📞 Support

If you encounter issues:

1. **Check Vercel documentation**: [vercel.com/docs](https://vercel.com/docs)
2. **Review function logs** in your Vercel dashboard
3. **Test with a small playlist** first
4. **Ensure YouTube Music headers are fresh**

---

**Happy transferring! 🎵✨**
