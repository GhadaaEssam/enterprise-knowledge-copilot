import streamlit as st

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.components.chat import render_chat
from app.components.evaluation import render_evaluation
from app.components.sidebar import render_sidebar
from app.components.monitoring import render_monitoring

st.set_page_config(
    page_title="Enterprise Knowledge Copilot",
    page_icon="🤖",
    layout="wide",
)

page = render_sidebar()

if page == "💬 Copilot":
    render_chat()

elif page == "📊 Evaluation":
    render_evaluation()

elif page == "📈 Monitoring":
    render_monitoring()