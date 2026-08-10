import os

import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from src.monitoring.tracker import MonitoringTracker
from src.agent.agent import KnowledgeAgent
from src.tools.handlers import (
    search_internal_documentation,
    search_web,
)
from src.tools.tool_registry import (
    INTERNAL_SEARCH_SCHEMA,
    WEB_SEARCH_SCHEMA,
    ToolRegistry,
)

@st.cache_resource
def create_agent() -> KnowledgeAgent:

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    groq_client = Groq(
        api_key=api_key
    )

    tool_registry = ToolRegistry()

    tool_registry.register(
        INTERNAL_SEARCH_SCHEMA,
        search_internal_documentation,
    )

    tool_registry.register(
        WEB_SEARCH_SCHEMA,
        search_web,
    )
    
    tracker = MonitoringTracker()

    return KnowledgeAgent(
        tool_registry=tool_registry,
        llm_client=groq_client,
        model="openai/gpt-oss-120b",
        tracker=tracker,
    )