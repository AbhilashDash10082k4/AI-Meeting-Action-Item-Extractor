"""
apps/streamlit/app.py

Purpose:
    Streamlit interactive dashboard UI for uploading transcripts and displaying extracted action items.

Working & Flow:
    - User uploads meeting transcript (.txt, .md, .docx, .pdf).
    - Makes HTTP POST request to FastAPI backend (`/api/v1/extract`). ZERO DIRECT DB CALLS.
    - Displays extracted action items in rich UI cards with status badges, owners, deadlines, and quote evidence.

Links to:
    - apps/api/routes/extraction_route.py
"""

import streamlit as st
import httpx

st.set_page_config(
    page_title="AI Meeting Action-Item Extractor",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stCard {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    .badge-owner {
        background-color: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .badge-status {
        background-color: #10b981;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .quote-box {
        border-left: 3px solid #6366f1;
        background: rgba(99, 102, 241, 0.1);
        padding: 8px 14px;
        margin-top: 10px;
        font-style: italic;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AI Meeting Action-Item Extractor")
st.caption("Upload meeting transcript (.txt, .md, .docx, .pdf) to extract grounded action items with evidence quotes.")

api_url = st.sidebar.text_input("API Base URL", value="http://localhost:8000")

uploaded_file = st.file_uploader(
    "Choose a transcript file",
    type=["txt", "md", "docx", "pdf"]
)

if uploaded_file is not None:
    if st.button("🚀 Extract Action Items", type="primary"):
        with st.spinner("Processing transcript & invoking extraction pipeline..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = httpx.post(f"{api_url}/api/v1/extract", files=files, timeout=60.0)

                if response.status_code == 200:
                    data = response.json()
                    action_items = data.get("action_items", [])
                    segments_count = data.get("segments_count", 0)

                    st.success(f"Extracted {len(action_items)} action item(s) from {segments_count} transcript segments!")

                    if not action_items:
                        st.info("No explicit action items found in transcript.")
                    else:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.subheader("📋 Extracted Action Items")
                            for idx, item in enumerate(action_items, 1):
                                with st.container():
                                    st.markdown(f"### {idx}. {item['task']}")
                                    mcol1, mcol2, mcol3 = st.columns(3)
                                    with mcol1:
                                        st.markdown(f"**Owner:** `{item.get('owner') or 'Unassigned'}`")
                                    with mcol2:
                                        st.markdown(f"**Deadline:** `{item.get('deadline') or 'None'}`")
                                    with mcol3:
                                        st.markdown(f"**Confidence:** `{int(item.get('confidence', 0) * 100)}%`")

                                    st.markdown(f"<div class='quote-box'><b>Evidence:</b> \"{item['evidence']}\"</div>", unsafe_allow_html=True)
                                    st.divider()

                        with col2:
                            st.subheader("📊 Summary Metrics")
                            st.metric("Total Tasks", len(action_items))
                            assigned_count = sum(1 for i in action_items if i.get("owner"))
                            st.metric("Assigned Tasks", assigned_count)
                            deadline_count = sum(1 for i in action_items if i.get("deadline"))
                            st.metric("Tasks with Deadline", deadline_count)

                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend API: {str(e)}")
