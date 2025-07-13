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
# Version: 2.6.1 (Update this number after each deployment)
# Last Updated: 2024-12-19
# Description: Streamlit web app for racing notes with Supabase backend
# ============================================================================

# Version Configuration - Update this for each deployment
APP_VERSION = "2.6.6"

# Set up environment variables for Streamlit Cloud
# These should be set in Streamlit Cloud's secrets management
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
SUPABASE_SERVICE_ROLE = st.secrets.get("SUPABASE_SERVICE_ROLE", os.getenv("SUPABASE_SERVICE_ROLE", ""))

# Import from moved modules - using absolute imports for Streamlit Cloud
import sys
import os

# Ensure current directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data.supabase_client import SupabaseClient
    from data.models import NoteCreate, NoteView, NoteCategory, Track, Series, Driver, Tag, SessionType
    from services.cloud_storage import CloudStorageService
except ImportError as e:
    import streamlit as st
    st.error(f"Import error: {e}")
    st.error("Please check that all required files are present in the deployment.")
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

# Initialize Supabase client
# supabase = SupabaseClient()
# supabase.connect()
# cloud_storage = CloudStorageService(supabase)

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
        /* Consolidated button styles */
        .stButton > button {
            background-color: #FFFFFF !important;  /* White background */
            color: #000000 !important;  /* Black text for readability */
            padding: 2px 6px !important;  /* Slightly more padding for readability */
            font-size: 10px !important;  /* Readable font size */
            border-radius: 4px !important;
            border: 1px solid #333333 !important;
            min-width: auto !important;
            height: 20px !important;  /* Fixed height for consistency */
            white-space: nowrap;
            font-weight: bold !important;
        }
        .stButton > button:hover {
            background-color: #F0F0F0 !important;
            color: #000000 !important;
            border-color: #000000 !important;
        }
        .stButton > button[type='primary'] {
            background-color: #1D9BF0 !important;  /* Blue for selected */
            color: white !important;
            border-color: #1D9BF0 !important;
        }
        .stButton > button[type='primary']:hover {
            background-color: #0C7ABF !important;
            color: white !important;
            border-color: #0C7ABF !important;
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
            .stButton > button {
                font-size: 8px !important;
                padding: 1px 4px !important;
                height: 18px !important;
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
            .stButton > button {
                font-size: 7px !important;
                padding: 1px 3px !important;
                height: 16px !important;
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
        st.text_input("Search Notes")

    # Main area: Compact note creation at top
    st.markdown('<div class="create-form">', unsafe_allow_html=True)
    st.header("What's happening?")  # X-like compose prompt
    body = st.text_area("Note Content", placeholder="Write your note...", height=100, label_visibility="collapsed")  # Compact text area with hidden label
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        track = st.selectbox("Track", options=[t.name for t in tracks], label_visibility="collapsed", index=[t.name for t in tracks].index(default_track) if default_track else 0)
    with col2:
        series = st.selectbox("Series", options=["CUP", "XFINITY", "TRUCK"], label_visibility="collapsed", index=["CUP", "XFINITY", "TRUCK"].index(default_series) if default_series else 0)
    with col3:
        session_type = st.selectbox("Session Type", options=[s.value for s in SessionType], label_visibility="collapsed", index=[s.value for s in SessionType].index(default_session_type) if default_session_type else 0)
    with col4:
        driver = st.selectbox("Driver (Optional)", options=["None"] + [d.name for d in drivers], label_visibility="collapsed")
    
    # Replace multiselect with small toggle buttons in two rows
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    def toggle_tag(label):
        if label in st.session_state.selected_tags:
            st.session_state.selected_tags.remove(label)
        else:
            st.session_state.selected_tags.append(label)
    
    # Split tags into two rows (with safety checks)
    if tags and len(tags) > 0:
        mid = len(tags) // 2
        row1_tags = tags[:mid]
        row2_tags = tags[mid:]
        
        # Row 1
        if len(row1_tags) > 0:
            cols1 = st.columns(len(row1_tags))
            for i, t in enumerate(row1_tags):
                with cols1[i]:
                    is_selected = t.label in st.session_state.selected_tags
                    st.button(t.label, key=f'tag_{t.id}_row1', on_click=toggle_tag, args=(t.label,), help='Selected' if is_selected else 'Not selected', type='primary' if is_selected else 'secondary')
        
        # Row 2
        if len(row2_tags) > 0:
            cols2 = st.columns(len(row2_tags))
            for i, t in enumerate(row2_tags):
                with cols2[i]:
                    is_selected = t.label in st.session_state.selected_tags
                    st.button(t.label, key=f'tag_{t.id}_row2', on_click=toggle_tag, args=(t.label,), help='Selected' if is_selected else 'Not selected', type='primary' if is_selected else 'secondary')
    else:
        st.info("No tags available - check Supabase connection")

    # Add media upload (always show)
    uploaded_files = st.file_uploader("Attach media", type=['jpg', 'png', 'gif', 'mp4', 'mov', 'avi'], accept_multiple_files=True, label_visibility="collapsed")
    
    # Post button
    if st.button("Post", type="primary"):
        if body.strip():
            # Find selected track and driver objects
            selected_track = next((t for t in tracks if t.name == track), None)
            selected_driver = next((d for d in drivers if d.name == driver), None) if driver != "None" else None
            
            # Create note
            note_create = NoteCreate(
                body=body,
                driver_id=selected_driver.id if selected_driver else None,
                category=NoteCategory.GENERAL,
                tag_ids=[tag.id for tag in tags if tag.label in st.session_state.selected_tags and tag.id is not None]
            )
            
            # Handle media files
            media_files = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    media_files.append({
                        'filename': uploaded_file.name,
                        'content': uploaded_file.read(),
                        'content_type': uploaded_file.type
                    })
            
            # Context info
            context_info = {
                'track_name': track,
                'series_name': series,
                'session_type': session_type,
                'driver_name': driver if driver != "None" else None,
                'tags': st.session_state.selected_tags
            }
            
            try:
                new_note = asyncio.run(supabase.create_note_with_context(note_create, context_info, media_files=media_files, created_by=st.session_state.current_user))
                if new_note:
                    st.success("Note posted!")
                    st.session_state.selected_tags = []  # Clear selections
                else:
                    st.error("Failed to post note - no response from database")
            except Exception as e:
                st.error(f"Error creating note: {str(e)}")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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