# Racing Notes Web App

A streamlined web application for managing racing notes, built with Streamlit and Supabase.

## 🚀 Live App

Access the live app at: [Your Streamlit Cloud URL]

## 📋 Current Version

**v2.6.1** - Tag readability improvements

## 🏗️ Architecture

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Supabase (PostgreSQL database + authentication)
- **Deployment**: Streamlit Cloud
- **Storage**: Supabase Storage for media files

## 📁 Project Structure

```
├── streamlit_app.py          # Main Streamlit application
├── data/                     # Database models and client
│   ├── models.py            # Pydantic models
│   ├── supabase_client.py   # Database client
│   └── cache.py             # Caching utilities
├── services/                # Business logic
│   ├── cloud_storage.py     # File upload/storage
│   └── data_service.py      # Data operations
├── .streamlit/              # Streamlit configuration
│   └── secrets.toml         # Environment variables (not in git)
├── supabase/               # Database schema
│   └── schema.sql          # Database structure
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Development Workflow

### Making Changes

1. **Edit the code** in `streamlit_app.py`
2. **Update the version** in the `APP_VERSION` variable at the top of the file
3. **Test locally** (optional): `streamlit run streamlit_app.py`
4. **Commit and push** to GitHub
5. **Streamlit Cloud automatically deploys** the changes

### Version Numbering

- Update `APP_VERSION = "x.x.x"` in `streamlit_app.py` after each change
- The version appears in the blue badge at the top of the app
- Use semantic versioning: major.minor.patch

### Quick Deploy Commands

```bash
# Make your changes, then:
git add .
git commit -m "Description of changes - bump to vX.X.X"
git push origin main
# Streamlit Cloud will automatically deploy
```

## 🔒 Environment Setup

Set these secrets in Streamlit Cloud:

```toml
# .streamlit/secrets.toml (for local development)
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-anon-key"
SUPABASE_SERVICE_ROLE = "your-service-role-key"
```

## 📊 Features

- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Real-time Notes** - Create and view racing notes instantly
- ✅ **Media Upload** - Attach photos and videos
- ✅ **Smart Filtering** - Filter by track, series, driver, tags
- ✅ **Tag System** - Organize notes with custom tags
- ✅ **User Management** - Multi-user support
- ✅ **Clean UI** - Twitter-like minimalist design

## 🔄 Recent Updates

- **v2.6.1**: Improved tag button readability and sizing
- **v2.6.0**: Added responsive design and version tracking
- **v2.5.0**: Reduced debug info and enhanced UI

## 📝 Database

The app uses Supabase with the following main tables:
- `notes` - Racing notes with metadata
- `tracks` - Racing tracks/venues
- `drivers` - Driver information
- `tags` - Note categorization tags
- `note_media` - Media file attachments

See `supabase/schema.sql` for the complete database structure.

## 🚨 Troubleshooting

- **Connection Issues**: Check Supabase credentials in Streamlit Cloud secrets
- **Import Errors**: Ensure all files are committed and pushed to GitHub
- **Version Not Updating**: Clear browser cache and check deployment logs

## 📞 Support

For issues or questions, check the Streamlit Cloud deployment logs or contact the development team. 