import streamlit as st
import os
from uuid import UUID
from typing import List, Optional
from app.data.supabase_client import SupabaseClient
from app.data.models import NoteCreate, NoteView, NoteCategory, Track, Series, Driver, Tag, SessionType
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import mimetypes
from app.services.cloud_storage import CloudStorageService

# Define relative_time early
def relative_time(dt: datetime) -> str:
    delta = datetime.now(dt.tzinfo) - dt
    days = delta.days
    if days > 0:
        return f"{days}d ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = delta.seconds // 60
    if minutes > 0:
        return f"{minutes}m ago"
    else:
        return f"{delta.seconds}s ago"

# Initialize Supabase client
load_dotenv()

# Debug: Show environment variables (safely)
st.write("=== DEBUG INFO ===")
st.write(f"SUPABASE_URL exists: {bool(os.getenv('SUPABASE_URL'))}")
st.write(f"SUPABASE_ANON_KEY exists: {bool(os.getenv('SUPABASE_ANON_KEY'))}")
supabase_url = os.getenv('SUPABASE_URL')
if supabase_url:
    st.write(f"SUPABASE_URL: {supabase_url[:30]}...")
else:
    st.error("SUPABASE_URL not found in environment!")

supabase = SupabaseClient()
supabase.connect()
st.write(f"Database connected: {supabase.is_connected}")
st.write(f"Supabase URL: {supabase.url[:20]}... (partial for security)")

cloud_storage = CloudStorageService(supabase)

# Fetch metadata
try:
    tracks = asyncio.run(supabase.get_tracks())
    st.write(f"✅ Loaded {len(tracks)} tracks")
except Exception as e:
    st.error(f"❌ Error loading tracks: {e}")
    tracks = []

try:
    drivers = asyncio.run(supabase.get_drivers())
    st.write(f"✅ Loaded {len(drivers)} drivers")
except Exception as e:
    st.error(f"❌ Error loading drivers: {e}")
    drivers = []

try:
    tags = asyncio.run(supabase.get_tags())
    st.write(f"✅ Loaded {len(tags)} tags")
except Exception as e:
    st.error(f"❌ Error loading tags: {e}")
    tags = []

st.write("=== END DEBUG INFO ===")
st.write(f"Loaded {len(tracks)} tracks, {len(drivers)} drivers, {len(tags)} tags from Supabase")

# Streamlit app title
st.title("Racing Notes Web App")
st.write("Web App Version: 0.3")

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
            background-color: #000000 !important;  /* Black background */
            color: white !important;  /* White text always */
            padding: 0px 2px !important;  /* Minimal padding */
            font-size: 8px !important;  /* Smaller font */
            border-radius: 4px !important;
            border: none !important;
            min-width: auto !important;
            height: auto !important;
            white-space: nowrap;
        }
        .stButton > button:hover {
            background-color: #333333 !important;
            color: white !important;
        }
        .stButton > button[type='primary'] {
            background-color: #1D9BF0 !important;  /* Blue for selected */
            color: white !important;
        }
        .stButton > button[type='primary']:hover {
            background-color: #0C7ABF !important;
            color: white !important;
        }
        /* Override for Post button to keep pill shape */
        button[kind='primary'] {
            background-color: #1D9BF0;
            color: white;
            border-radius: 9999px;  /* Pill shape */
            padding: 4px 12px;
            font-size: 14px;
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
    
    # Split tags into two rows
    mid = len(tags) // 2
    row1_tags = tags[:mid]
    row2_tags = tags[mid:]
    
    # Row 1
    cols1 = st.columns(len(row1_tags))
    for i, t in enumerate(row1_tags):
        with cols1[i]:
            is_selected = t.label in st.session_state.selected_tags
            st.button(t.label, key=f'tag_{t.id}_row1', on_click=toggle_tag, args=(t.label,), help='Selected' if is_selected else 'Not selected', type='primary' if is_selected else 'secondary')
    
    # Row 2
    cols2 = st.columns(len(row2_tags))
    for i, t in enumerate(row2_tags):
        with cols2[i]:
            is_selected = t.label in st.session_state.selected_tags
            st.button(t.label, key=f'tag_{t.id}_row2', on_click=toggle_tag, args=(t.label,), help='Selected' if is_selected else 'Not selected', type='primary' if is_selected else 'secondary')
    
    # Add media upload
    uploaded_files = st.file_uploader("Attach media", type=['jpg', 'png', 'gif', 'mp4', 'mov', 'avi'], accept_multiple_files=True, label_visibility="collapsed")
    
    if st.button("Post"):  # X-like button
        context_info = {
            'track': next(t for t in tracks if t.name == track),
            'series': series,
            'session_type': session_type
        }
        driver_id = next((d.id for d in drivers if d.name == driver), None) if driver != "None" else None
        selected_labels = st.session_state.selected_tags
        tag_ids = [t.id for t in tags if t.label in selected_labels and t.id is not None]
        note_create = NoteCreate(
            body=body,
            driver_id=driver_id,
            category=NoteCategory.GENERAL,
            tag_ids=tag_ids
        )
        
        # Handle media uploads
        media_files = []
        if uploaded_files:
            for file in uploaded_files:
                temp_path = os.path.join('/tmp', file.name)
                try:
                    with open(temp_path, 'wb') as f:
                        f.write(file.getvalue())
                    public_url = asyncio.run(cloud_storage.upload_file(temp_path))
                    if public_url:
                        file_info = cloud_storage.get_file_info(temp_path)
                        if file_info is not None:
                            file_info['cloud_url'] = public_url
                            file_info['storage_type'] = 'cloud'
                            media_files.append(file_info)
                        else:
                            st.error(f"Failed to get info for file {file.name}")
                    else:
                        st.error(f"Failed to upload file {file.name}")
                except Exception as e:
                    st.error(f"Error uploading {file.name}: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
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
    if notes:
        for note in notes:
            rel_time = relative_time(note.created_at)
            driver_str = f"Driver: {note.driver_name or 'N/A'}"
            track_str = f"Track: {note.track_name or 'N/A'}"
            session_str = f"Session: {note.session_type.value if note.session_type else 'N/A'} on {note.session_date or 'N/A'}"
            vehicle_str = f"{note.series_name or 'N/A'}"
            metadata = " · ".join([driver_str, track_str, session_str, vehicle_str])
            tags_str = " ".join([f"#{tag}" for tag in note.tags]) if note.tags else ""
            html = f"""
            <div class="note-card">
                <div class="header">
                    <span class="avatar">🧑</span>
                    <span class="author">{note.created_by}</span>
                    <span class="timestamp">· {rel_time}</span>
                </div>
                <p class="body">{note.body}</p>
                <p class="metadata">{metadata}</p>
                <p class="tags">{tags_str}</p>
                <div class="actions">
                    <span>💬</span> <span>🔁</span> <span>❤️</span> <span>📊</span> <span>🔖</span>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No notes yet. Post one above!") 