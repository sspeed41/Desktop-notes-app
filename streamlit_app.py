import streamlit as st
import os
from uuid import UUID
from typing import List, Optional
from datetime import datetime
import mimetypes
import asyncio

# ============================================================================
# RACING NOTES WEB APP - STREAMLIT CLOUD VERSION
# ============================================================================
# Version: 2.6.8 (Restored original with deployment fixes)
# Last Updated: 2024-12-19
# Description: Streamlit web app for racing notes with Supabase backend
# ============================================================================

# Version Configuration - Update this for each deployment
APP_VERSION = "2.10.8"

# Quick check for required directories
if not os.path.exists("data") or not os.path.exists("services"):
    st.error("❌ Required directories 'data' and 'services' not found!")
    st.error("Please ensure all files are properly uploaded to your repository.")
    st.stop()

# Set up environment variables for Streamlit Cloud
# These should be set in Streamlit Cloud's secrets management
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
SUPABASE_SERVICE_ROLE = st.secrets.get("SUPABASE_SERVICE_ROLE", os.getenv("SUPABASE_SERVICE_ROLE", ""))

# Import from modules - using absolute imports for Streamlit Cloud
import sys
import os

# Ensure current directory is in Python path for local development
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import required modules
try:
    from data.supabase_client import SupabaseClient
    from data.models import NoteCreate, NoteView, NoteCategory, Track, Series, Driver, Tag, SessionType
    from services.cloud_storage import CloudStorageService
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.error("Please check that all required files are present in the deployment.")
    st.error("Make sure you're using 'streamlit_app.py' as your main file path in Streamlit Cloud.")
    st.stop()

# Set up environment variables for SupabaseClient
os.environ["SUPABASE_URL"] = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
os.environ["SUPABASE_ANON_KEY"] = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
os.environ["SUPABASE_SERVICE_ROLE"] = st.secrets.get("SUPABASE_SERVICE_ROLE", os.getenv("SUPABASE_SERVICE_ROLE", ""))

# Now initialize SupabaseClient - it will use os.getenv
supabase = SupabaseClient()
supabase.connect()
cloud_storage = CloudStorageService(supabase)

# Define relative_time early
def relative_time(dt: datetime) -> str:
    delta = datetime.now(dt.tzinfo) - dt
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return f"{delta.seconds}s ago"

# Fetch metadata with error handling
tracks = []
drivers = []
tags = []

try:
    tracks = asyncio.run(supabase.get_tracks())
except Exception as e:
    st.warning(f"Failed to load tracks: {str(e)}")
    tracks = []

try:
    drivers = asyncio.run(supabase.get_drivers())
except Exception as e:
    st.warning(f"Failed to load drivers: {str(e)}")
    drivers = []

try:
    tags = asyncio.run(supabase.get_tags())
except Exception as e:
    st.warning(f"Failed to load tags: {str(e)}")
    tags = []

# Compact status indicator
status_icon = "🟢" if supabase.is_connected else "🔴"
st.markdown(f"""
<div style="font-size: 12px; color: #666; margin-bottom: 8px;">
    {status_icon} Connected • {len(tracks)} tracks • {len(drivers)} drivers • {len(tags)} tags
</div>
""", unsafe_allow_html=True)

# Streamlit app title
st.title("Racing Notes Web App")
st.markdown(f"""
<div style="display: inline-block; background: #1DA1F2; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-bottom: 16px;">
    v{APP_VERSION}
</div>
""", unsafe_allow_html=True)

# Custom CSS for X-like (Twitter) styling - minimalistic, compact, efficient
st.markdown("""
    <style>
        /* Global styles for minimalism */
        .stApp {
            background-color: #FFFFFF;  /* Light mode */
            color: #0F1419;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        /* Compact note creation form */
        .create-form {
            padding: 8px;
            border-bottom: 1px solid #EFF3F4;
            margin-bottom: 8px;
        }
        /* X-like note cards */
        .note-card {
            border-bottom: 1px solid #EFF3F4;  /* Divider style, no full border */
            padding: 8px 12px;
            margin: 0;
            display: flex;
            flex-direction: column;
        }
        .note-card:hover {
            background-color: #F7F9F9;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 2px;
        }
        .avatar {
            font-size: 16px;  /* Small avatar */
            margin-right: 8px;
        }
        .author {
            font-weight: bold;
            font-size: 14px;
            color: #0F1419;
        }
        .timestamp {
            font-size: 12px;
            color: #536471;
            margin-left: 4px;
        }
        .body {
            font-size: 14px;
            line-height: 18px;
            color: #0F1419;
            margin: 0 0 4px 0;
        }
        .metadata {
            font-size: 12px;
            color: #536471;
            margin: 2px 0;
        }
        .tags {
            font-size: 12px;
            color: #1D9BF0;  /* X blue */
        }
        .actions {
            display: flex;
            justify-content: space-between;
            max-width: 220px;
            margin-top: 4px;
            color: #536471;
            font-size: 13px;
        }
        /* Make selects and inputs more compact */
        .stSelectbox > div > div > div, .stTextArea > div > div > div {
            padding: 4px;
            font-size: 14px;
        }
        /* X/Twitter style pill tag buttons - Ultra compact and space-efficient */
        div[data-testid="stButton"] > button,
        .stButton > button,
        button[kind="secondary"] {
            background-color: #F7F9FA !important;  /* Very light gray like X */
            color: #536471 !important;  /* X gray text color */
            padding: 0px 4px !important;  /* Ultra compact padding */
            font-size: 8px !important;  /* Even smaller font size */
            border-radius: 4px !important;  /* Minimal rounded corners */
            border: 1px solid #E1E8ED !important;  /* Subtle border */
            min-width: auto !important;
            max-width: none !important;
            width: auto !important;
            height: 11px !important;  /* Much smaller height */
            white-space: nowrap !important;
            font-weight: 400 !important;  /* Normal weight like X */
            text-transform: none !important;
            line-height: 1 !important;
            box-sizing: border-box !important;
            transition: all 0.15s ease !important;  /* Quick smooth transitions */
            margin: 0.5px !important;  /* Ultra minimal spacing */
            display: inline-flex !important;  /* Better alignment */
            align-items: center !important;
            justify-content: center !important;
        }
        div[data-testid="stButton"] > button:hover,
        .stButton > button:hover,
        button[kind="secondary"]:hover {
            background-color: #E1E8ED !important;  /* Slightly darker on hover */
            color: #14171A !important;  /* Darker text on hover */
            border-color: #CCD6DD !important;
            transform: none !important;  /* No transform effects */
        }
        div[data-testid="stButton"] > button[type='primary'],
        .stButton > button[type='primary'],
        button[kind="primary"] {
            background-color: #1D9BF0 !important;  /* X blue for selected */
            color: white !important;
            border-color: #1D9BF0 !important;
            font-size: 8px !important;  /* Consistent small font */
            height: 11px !important;  /* Consistent small height */
            padding: 0px 4px !important;  /* Consistent padding */
            border-radius: 4px !important;  /* Minimal rounded corners */
        }
        div[data-testid="stButton"] > button[type='primary']:hover,
        .stButton > button[type='primary']:hover,
        button[kind="primary"]:hover {
            background-color: #1A91DA !important;  /* Slightly darker blue on hover */
            color: white !important;
            border-color: #1A91DA !important;
        }
        /* Override for Post button to keep pill shape */
        button[kind='primary'] {
            background-color: #1D9BF0;
            color: white;
            border-radius: 9999px;  /* Pill shape */
            padding: 4px 12px;
            font-size: 14px;
        }
        
        /* Mobile responsiveness for small screens and iPhones */
        @media (max-width: 768px) {
            .stApp {
                font-size: 12px;
                padding: 4px;
            }
            .note-card {
                padding: 4px 8px;
                margin: 2px 0;
            }
            .header {
                margin-bottom: 1px;
            }
            .author {
                font-size: 12px;
            }
            .timestamp {
                font-size: 10px;
            }
            .body {
                font-size: 12px;
                line-height: 16px;
            }
            .metadata {
                font-size: 10px;
            }
            .tags {
                font-size: 10px;
            }
            div[data-testid="stButton"] > button,
            .stButton > button,
            button[kind="secondary"],
            button[kind="primary"] {
                font-size: 7px !important;  /* Very small on mobile */
                padding: 0px 3px !important;  /* Ultra compact mobile padding */
                height: 10px !important;  /* Very small on mobile */
                margin: 0.5px !important;  /* Ultra minimal spacing */
                border-radius: 3px !important;  /* Maintain compact shape */
            }
            .stSelectbox > div > div > div {
                font-size: 12px;
                padding: 2px;
            }
            .stTextArea > div > div > div {
                font-size: 12px;
                padding: 2px;
            }
        }
        
        /* Extra small screens (iPhone SE, etc.) */
        @media (max-width: 480px) {
            .stApp {
                font-size: 11px;
                padding: 2px;
            }
            .note-card {
                padding: 2px 4px;
            }
            .author {
                font-size: 11px;
            }
            .body {
                font-size: 11px;
                line-height: 14px;
            }
            div[data-testid="stButton"] > button,
            .stButton > button,
            button[kind="secondary"],
            button[kind="primary"] {
                font-size: 6px !important;  /* Tiny but still readable */
                padding: 0px 2px !important;  /* Ultra minimal padding */
                height: 9px !important;  /* Smallest height */
                margin: 0.5px !important;  /* Ultra minimal spacing */
                border-radius: 2px !important;  /* Minimal rounded corners */
            }
        }
    </style>
""", unsafe_allow_html=True)

# Session state for current user
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# User selection
if st.session_state.current_user is None:
    user_options = ["Scott Speed", "Dan Stratton", "Josh Wise"]
    selected_user = st.selectbox("Select Note Taker", options=user_options + ["Other"])
    if selected_user == "Other":
        selected_user = st.text_input("Enter your name")
    if st.button("Confirm") and selected_user:
        st.session_state.current_user = selected_user
        st.rerun()
else:
    st.write(f"Logged in as: {st.session_state.current_user}")
    if st.button("Change User"):
        st.session_state.current_user = None
        st.rerun()

# Sidebar for defaults and potential filters (efficient navigation)
if st.session_state.current_user:
    with st.sidebar:
        st.header("Defaults & Filters")
        default_track = st.selectbox("Default Track", options=[t.name for t in tracks], key="default_track")
        default_series = st.selectbox("Default Series", options=["CUP", "XFINITY", "TRUCK"], key="default_series")
        default_session_type = st.selectbox("Default Session Type", options=[s.value for s in SessionType], key="default_session_type")
        # Placeholder for future filters
        st.subheader("Filters")
        search_text = st.text_input("Search Notes")
        
        # Media Search Section
        st.subheader("🎥 Media Search")
        st.caption("Find media by context")
        
        # Media search controls
        media_search_driver = st.selectbox("Search by Driver", options=["Any"] + [d.name for d in drivers], key="media_driver")
        media_search_track = st.selectbox("Search by Track", options=["Any"] + [t.name for t in tracks], key="media_track") 
        media_search_series = st.selectbox("Search by Series", options=["Any", "CUP", "XFINITY", "TRUCK"], key="media_series")
        media_search_tag = st.selectbox("Search by Tag", options=["Any"] + [t.label for t in tags], key="media_tag")
        
        if st.button("🔍 Search Media", key="search_media_btn"):
            # Build search criteria
            search_criteria = {}
            if media_search_driver != "Any":
                search_criteria['driver_name'] = media_search_driver
            if media_search_track != "Any":
                search_criteria['track_name'] = media_search_track
            if media_search_series != "Any":
                search_criteria['series_name'] = media_search_series
            if media_search_tag != "Any":
                search_criteria['tag_name'] = media_search_tag
            
            # Store search criteria in session state
            st.session_state.media_search_criteria = search_criteria
            st.session_state.show_media_results = True
            st.rerun()

    # Main area: Compact note creation at top
    st.markdown('<div class="create-form">', unsafe_allow_html=True)
    st.header("What's happening?")  # X-like compose prompt
    
    # Initialize note text in session state
    if 'note_text' not in st.session_state:
        st.session_state.note_text = ""
    
    body = st.text_area("Note Content", value=st.session_state.note_text, placeholder="Write your note...", height=100, label_visibility="collapsed")
    # Update session state with current text
    st.session_state.note_text = body
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        track = st.selectbox("Track", options=[t.name for t in tracks], label_visibility="collapsed", index=[t.name for t in tracks].index(default_track) if default_track else 0)
    with col2:
        series = st.selectbox("Series", options=["None (General)", "CUP", "XFINITY", "TRUCK"], label_visibility="collapsed", index=["None (General)", "CUP", "XFINITY", "TRUCK"].index(default_series) if default_series and default_series in ["CUP", "XFINITY", "TRUCK"] else 0)
    with col3:
        session_type = st.selectbox("Session Type", options=["None (General)"] + [s.value for s in SessionType], label_visibility="collapsed", index=(["None (General)"] + [s.value for s in SessionType]).index(default_session_type) if default_session_type and default_session_type in [s.value for s in SessionType] else 0)
    with col4:
        driver = st.selectbox("Driver (Optional)", options=["None"] + [d.name for d in drivers], label_visibility="collapsed")
    
    # Replace multiselect with small toggle buttons in a flowing layout
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    def toggle_tag(label):
        if label in st.session_state.selected_tags:
            st.session_state.selected_tags.remove(label)
        else:
            st.session_state.selected_tags.append(label)
    
    # Create a flowing layout with better spacing
    if tags and len(tags) > 0:
        # Create columns for tags with better space utilization
        tags_per_row = 8  # Increased from 6 to fit more tags per row
        for i in range(0, len(tags), tags_per_row):
            batch = tags[i:i + tags_per_row]
            cols = st.columns(len(batch))
            
            for j, tag in enumerate(batch):
                with cols[j]:
                    is_selected = tag.label in st.session_state.selected_tags
                    st.button(
                        tag.label, 
                        key=f'tag_{tag.id}_batch_{i//tags_per_row}_{j}', 
                        on_click=toggle_tag, 
                        args=(tag.label,), 
                        help='Selected' if is_selected else 'Not selected', 
                        type='primary' if is_selected else 'secondary'
                    )
    else:
        st.info("No tags available - check Supabase connection")

    # Add media upload (always show)
    # Initialize file uploader key in session state for clearing after post
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0
    
    uploaded_files = st.file_uploader(
        "Attach media", 
        type=['jpg', 'png', 'gif', 'mp4', 'mov', 'avi', 'csv', 'xlsx', 'xls'], 
        accept_multiple_files=True, 
        label_visibility="collapsed",
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )
    
    # Post button
    if st.button("Post", type="primary"):
        st.write("🔍 DEBUG: Post button clicked!")
        st.write(f"🔍 DEBUG: Body text: '{body.strip()}'")
        st.write(f"🔍 DEBUG: uploaded_files: {uploaded_files}")
        
        if body.strip():
            # Find selected track and driver objects
            selected_track = next((t for t in tracks if t.name == track), None)
            selected_driver = next((d for d in drivers if d.name == driver), None) if driver != "None" else None
            
            # Validate we have required data
            if not selected_track:
                st.error(f"❌ Track '{track}' not found in database")
                st.stop()
            
            # Create note
            note_create = NoteCreate(
                body=body,
                driver_id=selected_driver.id if selected_driver else None,
                category=NoteCategory.GENERAL,
                tag_ids=[tag.id for tag in tags if tag.label in st.session_state.selected_tags and tag.id is not None]
            )
            
            # Handle media files - SIMPLIFIED APPROACH
            media_files = []
            if uploaded_files:
                st.write(f"🔍 DEBUG: Found {len(uploaded_files)} uploaded files")
                for i, f in enumerate(uploaded_files):
                    st.write(f"   File {i+1}: {f.name} ({f.size} bytes, type: {f.type})")
                
                st.write(f"📁 Processing {len(uploaded_files)} file(s)...")
                
                for uploaded_file in uploaded_files:
                    st.write(f"🔍 DEBUG: Starting to process {uploaded_file.name}")
                    try:
                        # Get file info
                        file_size_mb = round(uploaded_file.size / (1024 * 1024), 2)
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        
                        # Determine media type (using only valid database enum values)
                        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                            media_type = "image"
                        elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                            media_type = "video"
                        elif file_ext in ['.csv', '.xlsx', '.xls']:
                            media_type = "csv"
                        else:
                            media_type = "image"  # Default fallback
                        
                        st.write(f"📤 Uploading {uploaded_file.name} ({file_size_mb} MB)...")
                        
                        # Save uploaded file to temporary location
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_file_path = tmp_file.name
                        
                        st.write(f"🔍 DEBUG: Saved to temp file: {tmp_file_path}")
                        
                        # Use the fixed CloudStorageService
                        try:
                            public_url = asyncio.run(cloud_storage.upload_file(tmp_file_path))
                            st.write(f"🔍 DEBUG: CloudStorageService raw return: {public_url}")
                            if not isinstance(public_url, str):
                                st.warning("⚠️ Public URL is not a string - attempting to convert")
                                public_url = str(public_url)
                            st.write(f"🔍 DEBUG: Final public URL: {public_url}")
                            
                            if public_url:
                                # Add to media files list
                                media_file = {
                                    'filename': uploaded_file.name,
                                    'file_url': public_url,
                                    'media_type': media_type,
                                    'size_mb': file_size_mb
                                }
                                media_files.append(media_file)
                                st.write(f"🔍 DEBUG: Added to media_files: {media_file}")
                                st.success(f"✅ Uploaded: {uploaded_file.name}")
                            else:
                                st.error(f"❌ Upload failed: No URL returned")
                                
                        finally:
                            # Clean up temp file
                            import os
                            try:
                                os.unlink(tmp_file_path)
                            except:
                                pass
                        
                    except Exception as e:
                        st.error(f"❌ Error uploading {uploaded_file.name}: {str(e)}")
                        continue
                
                st.write(f"📊 Successfully processed {len(media_files)} out of {len(uploaded_files)} files")
                
                # Debug: Show what we're about to pass to the database
                if media_files:
                    st.write("🔍 DEBUG: Media files to be attached:")
                    for i, media_file in enumerate(media_files, 1):
                        st.write(f"   {i}. {media_file['filename']} ({media_file['media_type']})")
                        st.write(f"      URL: {media_file['file_url']}")
                        st.write(f"      Size: {media_file['size_mb']} MB")
                else:
                    st.write("🔍 DEBUG: No media files to attach")
            else:
                st.write("🔍 DEBUG: No uploaded_files detected")
            
            # Context info
            context_info = {
                'track': selected_track,  # Pass track object instead of string
                'series': series if series != "None (General)" else None,  # Handle None selection
                'session_type': session_type if session_type != "None (General)" else None,  # Handle None selection
                'driver_name': driver if driver != "None" else None,
                'tags': st.session_state.selected_tags
            }
            
            # Show what we're about to create
            with st.spinner("Creating note..."):
                try:
                    new_note = asyncio.run(supabase.create_note_with_context(note_create, context_info, media_files=media_files, created_by=st.session_state.current_user))
                    if new_note:
                        st.success("✅ Note posted successfully!")
                        st.session_state.selected_tags = []  # Clear selections
                        st.session_state.note_text = "" # Clear the text area
                        st.session_state.file_uploader_key += 1 # Increment key to clear files
                    else:
                        st.error("❌ Failed to post note - no response from database")
                except Exception as e:
                    st.error(f"❌ Error creating note: {str(e)}")
                    st.error("Check your database connection and try again.")
            st.rerun()
        else:
            st.warning("⚠️ Please enter some text for your note")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Media Search Results Section
    if hasattr(st.session_state, 'show_media_results') and st.session_state.show_media_results:
        if hasattr(st.session_state, 'media_search_criteria'):
            search_criteria = st.session_state.media_search_criteria
            
            st.header("🎥 Media Search Results")
            
            # Build display title for search criteria
            criteria_parts = []
            if 'driver_name' in search_criteria:
                criteria_parts.append(f"Driver: {search_criteria['driver_name']}")
            if 'track_name' in search_criteria:
                criteria_parts.append(f"Track: {search_criteria['track_name']}")
            if 'series_name' in search_criteria:
                criteria_parts.append(f"Series: {search_criteria['series_name']}")
            if 'tag_name' in search_criteria:
                criteria_parts.append(f"Tag: {search_criteria['tag_name']}")
            
            criteria_text = " | ".join(criteria_parts) if criteria_parts else "All Media"
            st.caption(f"Searching for: {criteria_text}")
            
            # Search for media
            try:
                with st.spinner("Searching media..."):
                    media_results = asyncio.run(supabase.search_media_by_criteria(**search_criteria))
                
                if media_results:
                    st.success(f"Found {len(media_results)} media files")
                    
                    # Display media files in a grid
                    cols_per_row = 3
                    for i in range(0, len(media_results), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, media in enumerate(media_results[i:i+cols_per_row]):
                            with cols[j]:
                                # Media card
                                context = media['note_context']
                                media_type_icon = "🎥" if media['media_type'] == 'video' else "📷" if media['media_type'] == 'image' else "📄"
                                
                                st.markdown(f"""
                                <div style="border: 1px solid #E1E8ED; border-radius: 8px; padding: 8px; margin-bottom: 8px;">
                                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">
                                        {media_type_icon} {media['filename']}
                                    </div>
                                    <div style="font-size: 12px; color: #536471; margin-bottom: 4px;">
                                        📍 {context['track_name']} • 👤 {context['driver_name'] or 'No driver'}
                                    </div>
                                    <div style="font-size: 12px; color: #536471; margin-bottom: 4px;">
                                        🏎️ {context['series_name']} • ⏱️ {context['session_type']}
                                    </div>
                                    <div style="font-size: 11px; color: #536471; margin-bottom: 8px;">
                                        By {context['created_by']} • {media['size_mb']:.1f}MB
                                    </div>
                                    <div style="font-size: 10px; color: #1D9BF0; margin-bottom: 8px;">
                                        {' '.join([f'#{tag}' for tag in context['tags']]) if context['tags'] else 'No tags'}
                                    </div>
                                    <a href="{media['file_url']}" target="_blank" style="
                                        display: inline-block;
                                        background: #1D9BF0;
                                        color: white;
                                        padding: 4px 8px;
                                        border-radius: 4px;
                                        text-decoration: none;
                                        font-size: 12px;
                                    ">🔗 View File</a>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.info("No media found matching your search criteria")
                    
            except Exception as e:
                st.error(f"Error searching media: {str(e)}")
            
            # Add button to clear results
            if st.button("❌ Clear Results", key="clear_media_results"):
                st.session_state.show_media_results = False
                st.rerun()
    
    # Recent Notes feed - compact scrolling list
    st.header("Home")  # X-like
    try:
        notes = asyncio.run(supabase.get_notes(limit=20))
    except Exception as e:
        st.error(f"Error fetching notes: {str(e)}")
        notes = []
    
    for note in notes:
        # Note card
        st.markdown(f"""
        <div class="note-card">
            <div class="header">
                <div class="avatar">🏁</div>
                <div class="author">{note.created_by}</div>
                <div class="timestamp">{relative_time(note.created_at)}</div>
            </div>
            <div class="body">{note.body}</div>
            <div class="metadata">
                📍 {note.track_name or 'Unknown Track'} • 
                🏎️ {note.series_name or 'Unknown Series'} • 
                ⏱️ {note.session_type.value if note.session_type else 'Unknown Session'}
                {f' • 👤 {note.driver_name}' if note.driver_name else ''}
            </div>
            {f'<div class="tags">{"  ".join([f"#{tag}" for tag in note.tags]) if note.tags else ""}</div>' if note.tags else ''}
        </div>
        """, unsafe_allow_html=True) 