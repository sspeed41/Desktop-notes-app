# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. **Push to GitHub**
Make sure your code is pushed to a GitHub repository.

### 2. **Deploy to Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set the main file path to: `streamlit_app.py`
5. Click "Deploy"

### 3. **Configure Secrets**
In your Streamlit Cloud app settings:
1. Go to "Settings" → "Secrets"
2. Add your environment variables:

```toml
SUPABASE_URL = "your-actual-supabase-url"
SUPABASE_ANON_KEY = "your-actual-supabase-anon-key"
SUPABASE_SERVICE_ROLE = "your-actual-supabase-service-role-key"
```

### 4. **Access from iPhone**
Once deployed, you'll get a URL like: `https://your-app-name.streamlit.app`

You can access this URL from:
- ✅ Any web browser on iPhone/iPad
- ✅ Any desktop browser
- ✅ Small windows (responsive design)

### 5. **Features**
- 📱 **Mobile Responsive**: Works great on iPhone screens
- 🏷️ **Small Tag Buttons**: Half the size, much more readable
- 🎯 **Version Badge**: Shows v2.6.0 prominently
- 🧹 **Clean Interface**: Minimal debug info
- 🔄 **Real-time Updates**: Syncs with your Supabase database

### 6. **Usage**
1. Select your name (Scott Speed, Dan Stratton, Josh Wise)
2. Create racing notes with track, series, session type
3. Add tags with small, readable buttons
4. Upload media files (videos, images)
5. View your notes feed in Twitter-like format

---

**That's it! Your Racing Notes app will be live on the web and accessible from any device.** 🏁 