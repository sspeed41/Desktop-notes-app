import streamlit as st
import os
import asyncio
from uuid import UUID
from typing import List, Optional
from datetime import datetime

# ============================================================================
# RACING NOTES WEB APP - STREAMLIT CLOUD VERSION
# ============================================================================
# Version: 3.0.0 (Fresh start with cleaned code)
# Last Updated: 2024-12-19
# Description: Streamlit web app for racing notes with Supabase backend
# ============================================================================

# Version Configuration - Update this for each deployment
APP_VERSION = "3.0.0"

# Configure Streamlit page
st.set_page_config(
    page_title="Racing Notes",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INITIALIZATION & SETUP
# ============================================================================

def setup_environment():
    """Setup environment variables for Streamlit Cloud and local development"""
    # Get secrets from Streamlit Cloud or environment variables
    supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    supabase_anon_key = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
    supabase_service_role = st.secrets.get("SUPABASE_SERVICE_ROLE", os.getenv("SUPABASE_SERVICE_ROLE", ""))
    
    # Set environment variables for modules
    os.environ["SUPABASE_URL"] = supabase_url
    os.environ["SUPABASE_ANON_KEY"] = supabase_anon_key
    os.environ["SUPABASE_SERVICE_ROLE"] = supabase_service_role
    
    return supabase_url, supabase_anon_key, supabase_service_role

def check_required_directories():
    """Check for required directories and files"""
    if not os.path.exists("data") or not os.path.exists("services"):
        st.error("❌ Required directories 'data' and 'services' not found!")
        st.error("Please ensure all files are properly uploaded to your repository.")
        st.error("Make sure you're using 'streamlit_app.py' as your main file path in Streamlit Cloud.")
        st.stop()

def import_modules():
    """Import required modules with error handling"""
    try:
        from data.supabase_client import SupabaseClient
        from data.models import NoteCreate, NoteView, NoteCategory, Track, Series, Driver, Tag, SessionType
        from services.cloud_storage import CloudStorageService
        return SupabaseClient, NoteCreate, NoteView, NoteCategory, Track, Series, Driver, Tag, SessionType, CloudStorageService
    except ImportError as e:
        st.error(f"❌ Import error: {e}")
        st.error("Please check that all required files are present in the deployment.")
        st.error("Make sure you're using 'streamlit_app.py' as your main file path in Streamlit Cloud.")
        st.stop()

def initialize_database():
    """Initialize database connection and fetch metadata"""
    SupabaseClient, _, _, _, _, _, _, _, _, CloudStorageService = import_modules()
    
    # Initialize clients
    supabase = SupabaseClient()
    connection_success = supabase.connect()
    cloud_storage = CloudStorageService(supabase)
    
    # Fetch metadata with error handling
    tracks, drivers, tags = [], [], []
    
    if connection_success:
        try:
            tracks = asyncio.run(supabase.get_tracks())
        except Exception as e:
            st.warning(f"Failed to load tracks: {str(e)}")
        
        try:
            drivers = asyncio.run(supabase.get_drivers())
        except Exception as e:
            st.warning(f"Failed to load drivers: {str(e)}")
        
        try:
            tags = asyncio.run(supabase.get_tags())
        except Exception as e:
            st.warning(f"Failed to load tags: {str(e)}")
    
    return supabase, cloud_storage, tracks, drivers, tags

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def relative_time(dt: datetime) -> str:
    """Format datetime as relative time string"""
    delta = datetime.now(dt.tzinfo) - dt
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return f"{delta.seconds}s ago"

def toggle_tag(label: str):
    """Toggle tag selection state"""
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    if label in st.session_state.selected_tags:
        st.session_state.selected_tags.remove(label)
    else:
        st.session_state.selected_tags.append(label)

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header(connection_status: bool, tracks: List, drivers: List, tags: List):
    """Render app header with status and version"""
    st.title("🏁 Racing Notes")
    
    # Version badge
    st.markdown(f"""
    <div style="display: inline-block; background: #1DA1F2; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-bottom: 16px;">
        v{APP_VERSION}
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicator
    status_icon = "🟢" if connection_status else "🔴"
    st.markdown(f"""
    <div style="font-size: 12px; color: #666; margin-bottom: 16px;">
        {status_icon} Database • {len(tracks)} tracks • {len(drivers)} drivers • {len(tags)} tags
    </div>
    """, unsafe_allow_html=True)

def render_user_selection():
    """Render user selection interface"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if st.session_state.current_user is None:
        st.subheader("👤 Select User")
        user_options = ["Scott Speed", "Dan Stratton", "Josh Wise"]
        selected_user = st.selectbox("Choose your name:", options=user_options + ["Other"])
        
        if selected_user == "Other":
            selected_user = st.text_input("Enter your name:")
        
        if st.button("Continue", type="primary") and selected_user:
            st.session_state.current_user = selected_user
            st.rerun()
        
        return False
    else:
        # Show current user with option to change
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"👤 Logged in as: **{st.session_state.current_user}**")
        with col2:
            if st.button("Change"):
                st.session_state.current_user = None
                st.rerun()
        return True

def render_sidebar(tracks: List, drivers: List, tags: List):
    """Render sidebar with defaults and filters"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Default values
        st.subheader("Defaults")
        track_options = [t.name for t in tracks] if tracks else ["No tracks available"]
        default_track = st.selectbox("Track:", options=track_options, key="default_track")
        default_series = st.selectbox("Series:", options=["CUP", "XFINITY", "TRUCK"], key="default_series")
        default_session = st.selectbox("Session:", options=["Practice", "Qualifying", "Race"], key="default_session")
        
        # Future filters placeholder
        st.subheader("🔍 Filters")
        search_query = st.text_input("Search notes:")
        
        # Ensure we always return strings
        return (
            default_track or (tracks[0].name if tracks else "No tracks"),
            default_series or "CUP",
            default_session or "Practice",
            search_query or ""
        )

def render_tag_selector(tags: List):
    """Render tag selection buttons"""
    if not tags:
        st.info("No tags available - check database connection")
        return
    
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    st.write("**Tags:**")
    
    # Split tags into rows for better layout
    tags_per_row = 6
    for i in range(0, len(tags), tags_per_row):
        row_tags = tags[i:i + tags_per_row]
        cols = st.columns(len(row_tags))
        
        for j, tag in enumerate(row_tags):
            with cols[j]:
                is_selected = tag.label in st.session_state.selected_tags
                button_type = "primary" if is_selected else "secondary"
                st.button(
                    tag.label,
                    key=f'tag_{tag.id}_{i}_{j}',
                    on_click=toggle_tag,
                    args=(tag.label,),
                    type=button_type
                )

def render_note_creation_form(tracks: List, drivers: List, tags: List, supabase, default_track: str, default_series: str, default_session: str):
    """Render note creation form"""
    st.subheader("✍️ Create Note")
    
    # Check if we have required data
    if not tracks:
        st.warning("⚠️ No tracks available. Please check database connection.")
        return None
    
    # Main content area
    body = st.text_area("What's happening?", placeholder="Write your racing note...", height=100)
    
    # Form controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        track_options = [t.name for t in tracks]
        track_index = track_options.index(default_track) if default_track in track_options else 0
        track = st.selectbox("Track:", options=track_options, index=track_index)
    
    with col2:
        series_options = ["CUP", "XFINITY", "TRUCK"]
        series_index = series_options.index(default_series) if default_series in series_options else 0
        series = st.selectbox("Series:", options=series_options, index=series_index)
    
    with col3:
        session_options = ["Practice", "Qualifying", "Race"]
        session_index = session_options.index(default_session) if default_session in session_options else 0
        session_type = st.selectbox("Session:", options=session_options, index=session_index)
    
    with col4:
        driver_options = ["None"] + [d.name for d in drivers]
        driver = st.selectbox("Driver:", options=driver_options)
    
    # Tag selection
    render_tag_selector(tags)
    
    # Media upload
    uploaded_files = st.file_uploader(
        "📎 Attach Media",
        type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'],
        accept_multiple_files=True
    )
    
    # Submit button
    if st.button("🚀 Post Note", type="primary"):
        if body.strip():
            return create_note(body, track, series, session_type, driver, uploaded_files, tracks, drivers, tags, supabase)
        else:
            st.error("Please enter note content")
    
    return None

def create_note(body: str, track: str, series: str, session_type: str, driver: str, uploaded_files, tracks: List, drivers: List, tags: List, supabase):
    """Create a new note"""
    try:
        # Import models
        _, NoteCreate, _, NoteCategory, _, _, _, _, _, _ = import_modules()
        
        # Find selected track and driver objects
        selected_track = next((t for t in tracks if t.name == track), None)
        selected_driver = next((d for d in drivers if d.name == driver), None) if driver != "None" else None
        
        # Create note object
        note_create = NoteCreate(
            body=body,
            driver_id=selected_driver.id if selected_driver else None,
            category=NoteCategory.GENERAL,
            tag_ids=[tag.id for tag in tags if tag.label in st.session_state.get('selected_tags', []) and tag.id is not None]
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
            'tags': st.session_state.get('selected_tags', [])
        }
        
        # Create note
        new_note = asyncio.run(supabase.create_note_with_context(
            note_create, 
            context_info, 
            media_files=media_files, 
            created_by=st.session_state.current_user
        ))
        
        if new_note:
            st.success("✅ Note posted successfully!")
            st.session_state.selected_tags = []  # Clear selections
            return new_note
        else:
            st.error("❌ Failed to post note - no response from database")
            
    except Exception as e:
        st.error(f"❌ Error creating note: {str(e)}")
    
    return None

def render_notes_feed(supabase):
    """Render the notes feed"""
    st.subheader("📋 Recent Notes")
    
    try:
        notes = asyncio.run(supabase.get_notes(limit=20))
        
        if not notes:
            st.info("No notes found. Create your first note above!")
            return
        
        for note in notes:
            with st.container():
                # Note header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{note.created_by}** • {relative_time(note.created_at)}")
                with col2:
                    st.markdown(f"🏁 {note.track_name or 'Unknown'}")
                
                # Note content
                st.markdown(note.body)
                
                # Metadata
                metadata_parts = []
                if note.series_name:
                    metadata_parts.append(f"🏎️ {note.series_name}")
                if note.session_type:
                    metadata_parts.append(f"⏱️ {note.session_type.value}")
                if note.driver_name:
                    metadata_parts.append(f"👤 {note.driver_name}")
                
                if metadata_parts:
                    st.markdown(" • ".join(metadata_parts))
                
                # Tags
                if note.tags:
                    tag_display = " ".join([f"#{tag}" for tag in note.tags])
                    st.markdown(f"🏷️ {tag_display}")
                
                st.divider()
                
    except Exception as e:
        st.error(f"❌ Error loading notes: {str(e)}")

def render_custom_css():
    """Render custom CSS for styling"""
    st.markdown("""
    <style>
        /* Clean, modern styling */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* Compact buttons */
        .stButton > button {
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .stApp {
                padding: 1rem 0.5rem;
            }
        }
        
        /* Note styling */
        .stContainer {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function"""
    # Setup
    setup_environment()
    check_required_directories()
    render_custom_css()
    
    # Initialize database and get components
    supabase, cloud_storage, tracks, drivers, tags = initialize_database()
    
    # Render header
    render_header(supabase.is_connected, tracks, drivers, tags)
    
    # User selection
    if not render_user_selection():
        return
    
    # Sidebar
    default_track, default_series, default_session, search_query = render_sidebar(tracks, drivers, tags)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Note creation form
        new_note = render_note_creation_form(
            tracks, drivers, tags, supabase,
            default_track, default_series, default_session
        )
        
        if new_note:
            st.rerun()
    
    with col2:
        # Notes feed
        render_notes_feed(supabase)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main() 