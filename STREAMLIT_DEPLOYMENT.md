# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. **Push to GitHub**
Make sure your code is pushed to a GitHub repository.

### 2. **Deploy to Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. **IMPORTANT**: Set the main file path to: `streamlit_app.py` (not app.py!)
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

## 🐛 Troubleshooting

### "Main Module Not Found" Error
If you see this error:
1. ✅ Make sure your main file path is set to `streamlit_app.py` (not `app.py`)
2. ✅ Ensure all directories (`data/`, `services/`) are in your repository
3. ✅ Check that `requirements.txt` is in your repository root
4. ✅ Try redeploying after pushing any changes

### Import Errors
If you see import errors:
1. ✅ Check that all Python files are properly committed to your repository
2. ✅ Verify that `__init__.py` files exist in `data/` and `services/` directories
3. ✅ Make sure your secrets are configured correctly

### Can't Connect to Supabase
If you see connection errors:
1. ✅ Double-check your secrets configuration
2. ✅ Verify your Supabase URL and keys are correct
3. ✅ Make sure your Supabase project is active

---

**That's it! Your Racing Notes app will be live on the web and accessible from any device.** 🏁 

To install the programs mentioned in the Streamlit output (Xcode command line tools and the Watchdog module for better performance), follow these steps on your macOS system. These are optional but recommended by Streamlit for improved app reloading during development.

### 1. Install Xcode Command Line Tools
This provides essential developer tools that many Python packages (including Watchdog) rely on.
- Open your Terminal app.
- Run this command:
  ```
  xcode-select --install
  ```
- A popup window will appear asking to install the tools. Click "Install" and follow the prompts. It may take a few minutes to download and install (around 1-2 GB depending on your macOS version).
- If it's already installed, you'll see a message saying so—no harm done.

### 2. Install Watchdog
This is a Python module that helps Streamlit detect file changes more efficiently.
- In the same Terminal window, run:
  ```
  pip install watchdog
  ```
- If you have multiple Python versions or virtual environments, make sure you're in the right one (e.g., if you're using a virtualenv for your project, activate it first with `source venv/bin/activate` or similar).

After these installations, try running your Streamlit app again with `streamlit run streamlit_app.py` to see if performance improves. If you run into any errors during installation (e.g., permission issues), try adding `sudo` to the commands or let me know the exact error message for more help.

### Summary of Actions I've Taken So Far
- Performed a semantic search on `streamlit_app.py` to understand the app's structure and components.
- Ran the command `streamlit run streamlit_app.py` to test the app, which started successfully and provided local/network URLs, but was interrupted (no obvious errors in the partial output). 