import os
import re
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import database
import pipeline

# Initialize Database
database.init_db()

# Make uploads directory
os.makedirs(os.path.join("y:\\Meeting_Summarizer", "uploads"), exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# CSS Styling & Font Integration (Glassmorphism + Modern Dark Theme)
# =====================================================================

CSS_STYLES = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Patrick+Hand&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* Global styling rules */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: #fcfaf6 !important;
    background-image: radial-gradient(#2b221d 0.5px, transparent 0.5px), radial-gradient(#2b221d 0.5px, #fcfaf6 0.5px) !important;
    background-size: 20px 20px !important;
    background-position: 0 0, 10px 10px !important;
    opacity: 0.99;
    color: #2b221d !important;
}

/* Scrollbars styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #f7f4eb;
}
::-webkit-scrollbar-thumb {
    background: #2b221d;
    border: 2px solid #f7f4eb;
    border-radius: 5px;
}

/* Titles and Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Fredoka', sans-serif !important;
    font-weight: 700 !important;
    color: #2b221d !important;
}

.glow-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 42px;
    font-weight: 700;
    color: #2b221d !important;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    margin-bottom: 2px;
    letter-spacing: -0.5px;
}

/* Sidebar overrides: Tan/Brown binder leather book style */
[data-testid="stSidebar"] {
    background-color: #5d4037 !important;
    border-right: 10px solid #3e2723;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label {
    color: #eae1d8 !important;
    font-family: 'Outfit', sans-serif !important;
}

.sidebar-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 24px;
    font-weight: 700;
    color: #eae1d8;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Custom folder-divider index tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    background-color: transparent !important;
    border-bottom: 3px solid #2b221d !important;
    border-radius: 0px !important;
    padding: 0px !important;
    margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    white-space: pre-wrap;
    background-color: #eae4d9 !important;
    border: 2px solid #2b221d !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0px 0px !important;
    color: #2b221d !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 14px;
    padding: 0 20px;
    margin-bottom: -3px; /* overlap border */
    transition: background-color 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #dfd8cb !important;
    color: #000000 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #2b221d !important;
    border-bottom: 3px solid #ffffff !important;
    box-shadow: none !important;
}

/* Neobrutalist Lined Notebook Sheet cards */
.glass-card {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #2b221d !important;
    backdrop-filter: none !important;
    transition: all 0.2s ease;
}
.glass-card:hover {
    transform: translate(-1px, -1px);
    box-shadow: 5px 5px 0px #2b221d !important;
}
.glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card h5, .glass-card h6 {
    color: #2b221d !important;
    font-family: 'Fredoka', sans-serif !important;
}
.glass-card p, .glass-card li, .glass-card ol, .glass-card ul {
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18.5px !important;
    line-height: 1.5 !important;
    color: #2b221d !important;
}

/* Custom styled numeric metric cards as mini school book tags */
.custom-metric-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.custom-metric-card {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    padding: 14px 20px !important;
    text-align: left !important;
    box-shadow: 3px 3px 0px #2b221d !important;
}
.custom-metric-val {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #b91c1c !important; /* Retro red values */
    margin-bottom: 2px !important;
    font-family: 'Fredoka', sans-serif !important;
}
.custom-metric-lbl {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: #64748b !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Decisions & Questions (Rotated sticker style!) */
.decision-card {
    background: #e6fcf5 !important; /* Mint green */
    border: 2px dashed #059669 !important;
    border-left: 2px dashed #059669 !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    color: #065f46 !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
    transform: rotate(-1deg);
    box-shadow: 2px 2px 6px rgba(0,0,0,0.03) !important;
}
.question-card {
    background: #fffbeb !important; /* Sticky yellow */
    border: 2px dashed #d97706 !important;
    border-left: 2px dashed #d97706 !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    color: #78350f !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
    transform: rotate(1.5deg);
    box-shadow: 2px 2px 6px rgba(0,0,0,0.03) !important;
}

/* Timeline Cards */
.timeline-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.timeline-item {
    display: flex !important;
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    cursor: pointer !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    color: #2b221d !important;
    transition: all 0.2s ease !important;
    align-items: center !important;
}
.timeline-item:hover {
    background: #fafafa !important;
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0px #2b221d !important;
}
.timeline-active {
    background: #fffbeb !important;
    border-color: #d97706 !important;
    box-shadow: 3px 3px 0px #d97706 !important;
}
.timeline-time {
    font-weight: 700 !important;
    color: #1d4ed8 !important; /* Retro blue */
    min-width: 90px !important;
    font-size: 13px !important;
    font-family: 'Fredoka', sans-serif !important;
}
.timeline-title {
    font-weight: 600 !important;
    color: #2b221d !important;
    font-size: 14.5px !important;
    font-family: 'Outfit', sans-serif !important;
}
.timeline-desc {
    font-size: 15px !important;
    color: #64748b !important;
    font-family: 'Patrick Hand', cursive !important;
}

/* Searchable Transcript Chat Bubbles */
.chat-bubble {
    display: flex !important;
    flex-direction: column !important;
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    transition: all 0.2s ease !important;
}
.chat-bubble-highlighted {
    background: #faf5ff !important;
    border-color: #8b5cf6 !important;
    box-shadow: 3px 3px 0px #8b5cf6 !important;
}
.chat-header {
    display: flex !important;
    justify-content: space-between !important;
    margin-bottom: 4px !important;
    font-size: 12px !important;
}
.chat-speaker {
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
}
.chat-time {
    color: #64748b !important;
    font-family: 'Fredoka', sans-serif !important;
}
.chat-text {
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18.5px !important;
    line-height: 1.3 !important;
    color: #2b221d !important;
}

/* Search Query Highlights */
.highlight {
    background-color: #fef08a !important; /* Highlighter yellow */
    border-bottom: 2px solid #eab308 !important;
    padding: 0 2px !important;
    border-radius: 2px !important;
    color: #000000 !important;
}

/* Sidebar sticker-like buttons */
[data-testid="stSidebar"] button {
    background-color: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    color: #2b221d !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] button:hover {
    transform: translate(-1px, -1px);
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #b91c1c !important;
}

/* Input boxes & Dropdowns notebook look */
.stTextInput input, .stSelectbox select, [data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    color: #2b221d !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
}

/* Checklist custom styling */
.action-row {
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
}

/* Priority tags as mini labels */
.tag-high {
    background: #fee2e2 !important;
    color: #ef4444 !important;
    border: 2px solid #ef4444 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-medium {
    background: #fef3c7 !important;
    color: #d97706 !important;
    border: 2px solid #d97706 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-low {
    background: #dbeafe !important;
    color: #2563eb !important;
    border: 2px solid #2563eb !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-positive {
    background: #e6fcf5 !important;
    color: #059669 !important;
    border: 2px solid #059669 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-neutral {
    background: #f1f5f9 !important;
    color: #64748b !important;
    border: 2px solid #64748b !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-negative {
    background: #fee2e2 !important;
    color: #ef4444 !important;
    border: 2px solid #ef4444 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Sidebar button text contrast fix */
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div {
    color: #2b221d !important;
}

/* Style Streamlit containers with border=True to look like neobrutalist glass cards */
div[data-testid="stVerticalBlockBorder"] {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #2b221d !important;
    backdrop-filter: none !important;
    transition: all 0.2s ease;
}
</style>
"""

# Inject custom CSS
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# =====================================================================
# Document Parsing Helpers
# =====================================================================

def parse_context_document(uploaded_file):
    """Extracts text content from TXT, MD, or PDF documents."""
    if uploaded_file is None:
        return None
        
    filename = uploaded_file.name
    if filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except ImportError:
            st.error("pypdf is required to parse PDF documents. Please check installation.")
            return "Error: pypdf not available."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    else:
        # Txt / Md fallback
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Error reading text document: {str(e)}"

# =====================================================================
# Session State Initialization
# =====================================================================

if "active_meeting_id" not in st.session_state:
    st.session_state.active_meeting_id = None
if "api_provider" not in st.session_state:
    st.session_state.api_provider = "Gemini"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3.5-flash"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =====================================================================
# Helper Formatting Functions
# =====================================================================

def format_duration(seconds):
    """Formats duration in seconds to MM:SS."""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def time_str_to_seconds(t_str):
    """Converts a standard clock string like '1:30' to float seconds."""
    try:
        parts = list(map(int, t_str.split(':')))
        if len(parts) == 2:
            return float(parts[0] * 60 + parts[1])
        elif len(parts) == 3:
            return float(parts[0] * 3600 + parts[1] * 60 + parts[2])
        return float(t_str)
    except Exception:
        return 0.0

def highlight_text(text, query):
    """Inserts mark tags for matching search text."""
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark class='highlight'>{m.group(0)}</mark>", text)

# Map speakers to consistent notebook ink colors
def get_speaker_color(speaker):
    speaker_colors = {
        "Sarah (PM)": "#b91c1c",        # Primary Red ink
        "David (Backend)": "#1d4ed8",   # Primary Blue ink
        "Alex (Frontend)": "#047857",  # Primary Green ink
        "Sarah": "#b91c1c",
        "David": "#1d4ed8",
        "Alex": "#047857"
    }
    if speaker in speaker_colors:
        return speaker_colors[speaker]
    
    # Dynamic fallback based on speaker hashing
    colors = ["#b91c1c", "#1d4ed8", "#047857", "#b45309", "#6b21a8"]
    import hashlib
    idx = int(hashlib.md5(speaker.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

# =====================================================================
# Sidebar: Logo, Past Meetings & Settings
# =====================================================================

with st.sidebar:
    st.markdown("<div class='sidebar-title'>🧠 Meeting Summarizer</div>", unsafe_allow_html=True)
    
    # Quick start Demo button
    if st.button("✨ Load Demo Meeting", use_container_width=True):
        # Generate and save demo meeting
        demo_data = pipeline.get_demo_meeting_data()
        
        # Save to DB
        demo_id = database.save_meeting(
            title="Meeting Summarizer: Product Kickoff & Planning",
            date=datetime.now().strftime("%Y-%m-%d"),
            duration_seconds=240,
            audio_path=None,
            transcript=demo_data["transcript"],
            analysis=demo_data["analysis"],
            context_doc_name="product_spec.md",
            context_doc_text="Meeting Summarizer is an advanced, high-performance meeting intelligence dashboard that goes far beyond basic summarization. Built in Python/Streamlit."
        )
        st.session_state.active_meeting_id = demo_id
        st.success("Demo meeting loaded!")
        st.rerun()

    st.markdown("---")
    
    # Past Meetings List
    st.markdown("### 🎬 Saved Meetings")
    meetings = database.get_all_meetings()
    
    if not meetings:
        st.markdown("<span style='color: #64748b; font-size: 12px;'>No processed meetings yet.</span>", unsafe_allow_html=True)
    else:
        for m in meetings:
            col_sel, col_del = st.columns([4, 1])
            with col_sel:
                # Highlight active meeting
                is_active = (st.session_state.active_meeting_id == m["id"])
                btn_label = f"📁 {m['title'][:25]}..." if len(m['title']) > 25 else f"📁 {m['title']}"
                if st.button(
                    btn_label, 
                    key=f"meeting_btn_{m['id']}", 
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.active_meeting_id = m["id"]
                    st.session_state.selected_topic = None
                    st.session_state.search_query = ""
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_btn_{m['id']}", help="Delete meeting"):
                    database.delete_meeting(m["id"])
                    if st.session_state.active_meeting_id == m["id"]:
                        st.session_state.active_meeting_id = None
                    st.rerun()

# =====================================================================
# Main Application Flow
# =====================================================================

if st.session_state.active_meeting_id is None:
    # -----------------------------------------------------------------
    # UPLOAD & ANALYZE TAB
    # -----------------------------------------------------------------
    
    st.markdown("<div class='glow-title'>Meeting Summarizer</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 15px; color: #64748b; margin-top:-10px; margin-bottom: 25px;'>Premium meeting intelligence dashboard powered by advanced multi-modal models.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>💡 Welcome to Meeting Summarizer</h4>
        <p>This intelligent dashboard processes meeting audio, performs diarized speaker transcription, identifies key decisions, compiles action lists, structures segmented topics, and powers interactive RAG context Q&A.</p>
        <p style='color: #b91c1c;'><b>How to start:</b></p>
        <ol>
            <li>Upload your meeting audio recording (.mp3, .wav, or .m4a).</li>
            <li>Optionally upload standard project documentation (e.g., specifications, transcripts, context briefs) to guide RAG context chat.</li>
            <li>Click <b>Analyze Meeting</b> to construct your intelligence dashboard.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col_file, col_opts = st.columns([2, 1])
    
    with col_file:
        with st.container(border=True):
            st.markdown("<h4>📤 Upload Audio File</h4>", unsafe_allow_html=True)
            uploaded_audio = st.file_uploader(
                "Choose a meeting audio recording", 
                type=["mp3", "wav", "m4a"],
                help="Files up to 100MB supported."
            )
            
            st.markdown("<h4>📄 Optional Context Document</h4>", unsafe_allow_html=True)
            uploaded_context = st.file_uploader(
                "Provide project spec or supplementary documents (for RAG context)", 
                type=["txt", "md", "pdf"],
                help="Supported file types: Text (.txt), Markdown (.md), PDF (.pdf)"
            )
        
    with col_opts:
        with st.container(border=True):
            st.markdown("<h4>📝 Meeting Details</h4>", unsafe_allow_html=True)
            meeting_title = st.text_input("Meeting Title", value=f"Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            meeting_date = st.date_input("Meeting Date", value=datetime.now().date())
            
            st.markdown("---")
            
            # Action button
            analyze_btn = st.button("🚀 Analyze Meeting", use_container_width=True, type="primary")
            
    if analyze_btn:
        # Validation checks
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            st.error("Error: GEMINI_API_KEY or GOOGLE_API_KEY is not set in the environment or .env file. Please configure the key on the server to enable live audio processing.")
            st.stop()
                 
        if not uploaded_audio:
            st.error("Please upload an audio file to run the analysis.")
            st.stop()
            
        with st.status("Initializing meeting intelligence pipeline...", expanded=True) as status:
            temp_audio_path = None
            doc_text = None
            doc_name = None
            
            # Save audio if uploaded
            if uploaded_audio:
                status.write("Saving uploaded audio file...")
                temp_audio_path = os.path.join("y:\\Meeting_Summarizer\\uploads", uploaded_audio.name)
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                    
            # Parse context document if present
            if uploaded_context:
                status.write("Extracting context document data...")
                doc_name = uploaded_context.name
                doc_text = parse_context_document(uploaded_context)
                
            status.write("Executing pipeline (Gemini pathway)...")
            
            try:
                # Process audio file through pipeline
                result = pipeline.process_audio(
                    audio_path=temp_audio_path,
                    provider="Gemini",
                    api_key=api_key,
                    model_name=st.session_state.get("selected_model", "gemini-3.5-flash")
                )
                
                status.write("Saving meeting details to database...")
                # Calculate dynamic duration using mutagen
                duration = 240
                if temp_audio_path:
                    try:
                        from mutagen import File
                        audio = File(temp_audio_path)
                        if audio is not None and audio.info is not None:
                            duration = int(audio.info.length)
                    except Exception as e:
                        pass
                    
                # Save details
                saved_id = database.save_meeting(
                    title=meeting_title,
                    date=meeting_date.strftime("%Y-%m-%d"),
                    duration_seconds=duration,
                    audio_path=temp_audio_path,
                    transcript=result["transcript"],
                    analysis=result["analysis"],
                    context_doc_name=doc_name,
                    context_doc_text=doc_text
                )
                
                status.update(label="Meeting Intelligence extraction successful!", state="complete")
                st.session_state.active_meeting_id = saved_id
                st.session_state.selected_topic = None
                st.session_state.search_query = ""
                st.rerun()
                
            except Exception as e:
                status.update(label="Analysis pipeline failed!", state="error")
                st.error(f"Error details: {str(e)}")

else:
    # -----------------------------------------------------------------
    # DASHBOARD OVERVIEW & TABS
    # -----------------------------------------------------------------
    
    # Load Active Meeting
    meeting = database.get_meeting_details(st.session_state.active_meeting_id)
    if not meeting:
        st.session_state.active_meeting_id = None
        st.error("Error loading meeting details. Returning to home.")
        st.stop()
        
    analysis = meeting["analysis"]
    transcript = meeting["transcript"]
    
    # Top banner layout
    col_title, col_back = st.columns([5, 1])
    with col_title:
        st.markdown(f"<div class='glow-title'>{meeting['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; font-size: 13px; margin-top:-10px; margin-bottom: 25px;'>📅 Date: {meeting['date']} | ⏰ Created At: {meeting['created_at']}</p>", unsafe_allow_html=True)
    with col_back:
        if st.button("⬅️ Upload New", use_container_width=True):
            st.session_state.active_meeting_id = None
            st.rerun()
            
    # TAB SEGMENTATION
    tab_dash, tab_transcript, tab_chat = st.tabs([
        "📊 Dashboard Overview",
        "💬 Searchable Dialogue Transcript",
        "🤖 Ask AI (RAG Chat)"
    ])
    
    # -----------------------------------------------------------------
    # TAB 1: DASHBOARD OVERVIEW
    # -----------------------------------------------------------------
    with tab_dash:
        # Custom metric cards grid
        st.markdown(f"""
        <div class='custom-metric-container'>
            <div class='custom-metric-card'>
                <div class='custom-metric-val'>{format_duration(meeting['duration_seconds'])}</div>
                <div class='custom-metric-lbl'>Meeting Duration</div>
            </div>
            <div class='custom-metric-card' style='border-bottom-color: #00f2fe;'>
                <div class='custom-metric-val'>{len(transcript)}</div>
                <div class='custom-metric-lbl'>Dialogue Entries</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_summary, col_objectives = st.columns([1, 1])
        
        with col_summary:
            st.markdown(f"""
            <div class='glass-card' style='height: 100%;'>
                <h4>📝 Executive Summary</h4>
                <p style='font-size: 14.5px; line-height: 1.6; color: #2b221d;'>{analysis.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_objectives:
            obj_list_html = "".join([f"<li style='margin-bottom: 8px;'>🎯 {obj}</li>" for obj in analysis.get('objectives', [])])
            st.markdown(f"""
            <div class='glass-card' style='height: 100%;'>
                <h4>🎯 Meeting Objectives</h4>
                <ul style='list-style-type: none; padding-left: 0; font-size: 14.5px; line-height: 1.6; color: #2b221d;'>
                    {obj_list_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Key Decisions & Action Items Section
        st.markdown("<br>", unsafe_allow_html=True)
        col_decisions, col_actions = st.columns([1, 1])
        
        with col_decisions:
            st.markdown("<h3>🎯 Key Decisions</h3>", unsafe_allow_html=True)
            decisions = analysis.get("key_decisions", [])
            if not decisions:
                st.markdown("<p style='color: #64748b; font-family: Outfit;'>No key decisions identified yet.</p>", unsafe_allow_html=True)
            else:
                for dec in decisions:
                    st.markdown(f"""
                    <div class='decision-card'>
                        📌 {dec}
                    </div>
                    """, unsafe_allow_html=True)
                    
        with col_actions:
            st.markdown("<h3>✅ Action Items Checklist</h3>", unsafe_allow_html=True)
            actions = analysis.get("action_items", [])
            if not actions:
                st.markdown("<p style='color: #64748b; font-family: Outfit;'>No action items identified yet.</p>", unsafe_allow_html=True)
            else:
                for i, act in enumerate(actions):
                    task = act.get("task", "")
                    owner = act.get("owner", "Unassigned")
                    due = act.get("due_date", "N/A")
                    priority = act.get("priority", "Medium")
                    confidence = act.get("confidence", 100)
                    
                    priority_class = f"tag-{priority.lower()}"
                    
                    st.markdown(f"""
                    <div class='action-row' style='border: 2px solid #2b221d; border-radius: 8px; padding: 12px; margin-bottom: 12px; box-shadow: 2px 2px 0px #2b221d; background: #ffffff;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                            <span class='{priority_class}'>{priority.upper()} PRIORITY</span>
                            <span style='font-size: 11px; color: #64748b; font-family: Outfit;'>Confidence: {confidence}%</span>
                        </div>
                        <div style='font-family: Patrick Hand, cursive; font-size: 18px; margin: 6px 0; color: #2b221d;'>📌 {task}</div>
                        <div style='display: flex; justify-content: space-between; font-size: 12px; color: #64748b; font-family: Outfit;'>
                            <span>👤 Owner: <b>{owner}</b></span>
                            <span>📅 Due: <b>{due}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Topics Timeline & Speaker Analytics Section
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_timeline, col_analytics = st.columns([1, 1])
        
        with col_timeline:
            st.markdown("<h3>📅 Discussion Timeline</h3>", unsafe_allow_html=True)
            topics = analysis.get("topics", [])
            if not topics:
                st.markdown("<p style='color: #64748b; font-family: Outfit;'>No discussion segments identified yet.</p>", unsafe_allow_html=True)
            else:
                for top in topics:
                    title = top.get("topic", "")
                    summary = top.get("summary", "")
                    start = top.get("start_time", "0:00")
                    end = top.get("end_time", "0:00")
                    
                    st.markdown(f"""
                    <div class='timeline-item'>
                        <div class='timeline-time'>⏳ {start} - {end}</div>
                        <div style='flex-grow: 1;'>
                            <div class='timeline-title'>{title}</div>
                            <div class='timeline-desc'>{summary}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with col_analytics:
            st.markdown("<h3>📊 Speaker Analytics</h3>", unsafe_allow_html=True)
            analytics = analysis.get("speaker_analytics", [])
            if not analytics:
                st.markdown("<p style='color: #64748b; font-family: Outfit;'>No speaker analytics available.</p>", unsafe_allow_html=True)
            else:
                df = pd.DataFrame(analytics)
                
                # List each speaker sentiment and details
                for i, row in df.iterrows():
                    sp = row.get("speaker", "")
                    words = row.get("words_spoken", 0)
                    pct = row.get("talk_percentage", 0.0)
                    sent = row.get("sentiment", "Neutral")
                    
                    sp_color = get_speaker_color(sp)
                    sent_tag = f"tag-{sent.lower()}" if sent.lower() in ["positive", "neutral", "negative"] else "tag-neutral"
                    
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; align-items: center; border: 2px solid #2b221d; border-radius: 8px; padding: 10px; margin-bottom: 8px; background: #ffffff; box-shadow: 2px 2px 0px #2b221d;'>
                        <span style='font-family: Outfit; font-weight: 700; color: {sp_color};'>👤 {sp}</span>
                        <span style='font-family: Outfit; font-size: 13px; color: #64748b;'>Words: <b>{words}</b> ({pct:.1f}%)</span>
                        <span class='{sent_tag}' style='padding: 2px 6px; font-size: 10px;'>{sent.upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Render pie chart for talk percentage
                try:
                    fig_pie = px.pie(
                        df, 
                        values='talk_percentage', 
                        names='speaker', 
                        title='Speaking Share (%)',
                        color_discrete_sequence=px.colors.qualitative.Safe
                    )
                    fig_pie.update_layout(
                        margin=dict(l=10, r=10, t=30, b=10),
                        height=220,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Outfit", size=11, color="#2b221d")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not render speaker chart: {e}")

    # -----------------------------------------------------------------
    # TAB 2: TRANSCRIPT
    # -----------------------------------------------------------------
    with tab_transcript:
        with st.container(border=True):
            st.markdown("<h4>💬 Dialogue Transcript</h4>", unsafe_allow_html=True)
            
            # Text search input
            search_query_input = st.text_input(
                "Search Transcript Text", 
                value=st.session_state.search_query, 
                placeholder="Type query to find and highlight matches...",
                key="transcript_search_input"
            )
            st.session_state.search_query = search_query_input
            
            st.markdown("---")
            
            # Rendering chat bubbles
            st.markdown("<div style='max-height: 480px; overflow-y: auto; padding-right: 8px;'>", unsafe_allow_html=True)
            
            found_any = False
            for idx, entry in enumerate(transcript):
                start = entry.get('start', 0.0)
                end = entry.get('end', 0.0)
                
                # Check search keyword match
                match_search = True
                if st.session_state.search_query:
                    if st.session_state.search_query.lower() not in entry.get('text', '').lower():
                        match_search = False
                        
                if not match_search:
                    continue
                    
                found_any = True
                highlighted_body = highlight_text(entry.get('text', ''), st.session_state.search_query)
                sp_color = get_speaker_color(entry.get('speaker'))
                
                st.markdown(f"""
                <div class='chat-bubble'>
                    <div class='chat-header'>
                        <span class='chat-speaker' style='color: {sp_color} !important;'>👤 {entry.get('speaker')}</span>
                        <span class='chat-time'>⏳ {format_duration(start)}</span>
                    </div>
                    <div class='chat-text'>{highlighted_body}</div>
                </div>
                """, unsafe_allow_html=True)
                
            if not found_any:
                st.markdown("<p style='color: #64748b; text-align: center; margin: 40px 0; font-family: Outfit, sans-serif;'>No transcript dialog segments match search term.</p>", unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 3: ASK AI (RAG CHAT)
    # -----------------------------------------------------------------
    with tab_chat:
        with st.container(border=True):
            st.markdown("<h4>🤖 Ask AI Meeting Assistant</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; color: #64748b; margin-top:-5px;'>Query specific statements, decisions, or timeline events from this meeting.</p>", unsafe_allow_html=True)
            
            meeting_id = str(meeting["id"])
            if meeting_id not in st.session_state.chat_history:
                st.session_state.chat_history[meeting_id] = [
                    {
                        "role": "assistant",
                        "content": f"Hello! I am your Meeting Intelligence assistant. Ask me anything about the meeting **'{meeting['title']}'**. I have access to the transcript and any uploaded supplementary document."
                    }
                ]
                
            # Display chat messages
            for msg in st.session_state.chat_history[meeting_id]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # Input query
            user_input = st.chat_input("What would you like to know about this meeting?")
            if user_input:
                # Add user query to chat history
                st.session_state.chat_history[meeting_id].append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Fetch live or demo answer
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
                
                with st.spinner("Analyzing meeting context..."):
                    try:
                        response_text = pipeline.answer_rag_query(
                            query=user_input,
                            transcript=transcript,
                            analysis=analysis,
                            context_doc_text=meeting.get("context_doc_text"),
                            provider="Gemini",
                            api_key=api_key,
                            model_name=st.session_state.get("selected_model", "gemini-3.5-flash")
                        )
                    except Exception as e:
                        response_text = f"An error occurred while calling the LLM: {str(e)}"
                
                # Add response to history
                st.session_state.chat_history[meeting_id].append({"role": "assistant", "content": response_text})
                st.rerun()
