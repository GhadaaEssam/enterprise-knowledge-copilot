import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("🤖 Knowledge Copilot")

        st.caption(
            "Enterprise knowledge assistant"
        )

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "💬 Copilot",
                "📊 Evaluation",
                "📈 Monitoring",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        st.markdown("**Knowledge Sources**")

        st.markdown("📚 Internal documentation")
        st.markdown("🌐 Web search")

        st.divider()

        if st.button(
            "🗑️ Clear conversation",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()

    return page