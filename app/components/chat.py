import streamlit as st

from app.components.agent_activity import render_agent_activity
from app.components.sources import render_sources
from app.utils.agent import create_agent


def render_chat():

    agent = create_agent()

    st.title("Enterprise Knowledge Copilot")

    st.caption(
        "Ask questions about your engineering "
        "documentation and get grounded answers."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "feedback" not in st.session_state:
        st.session_state.feedback = {}

    # ========================================================
    # Existing conversation
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            # ------------------------------------------------
            # Assistant-specific content
            # ------------------------------------------------

            if message["role"] == "assistant":

                tool_calls = message.get(
                    "tool_calls",
                    [],
                )

                request_id = message.get(
                    "request_id"
                )

                # Agent activity
                if tool_calls:

                    with st.expander(
                        "🔍 Agent activity"
                    ):
                        render_agent_activity(
                            tool_calls
                        )

                    # Sources
                    with st.expander(
                        "📚 Sources"
                    ):
                        render_sources(
                            tool_calls
                        )

                # ------------------------------------------------
                # Feedback
                # ------------------------------------------------

                if request_id:

                    current_feedback = (
                        st.session_state.feedback.get(
                            request_id
                        )
                    )

                    if current_feedback:

                        if current_feedback == "like":

                            st.caption(
                                "👍 Thanks for your feedback!"
                            )

                        elif current_feedback == "dislike":

                            st.caption(
                                "👎 Thanks for your feedback!"
                            )

                    else:

                        st.caption(
                            "Was this answer helpful?"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "👍",
                                key=f"like_{request_id}",
                            ):

                                agent.tracker.record_feedback(
                                    request_id=request_id,
                                    feedback="like",
                                )

                                st.session_state.feedback[
                                    request_id
                                ] = "like"

                                st.rerun()

                        with col2:

                            if st.button(
                                "👎",
                                key=f"dislike_{request_id}",
                            ):

                                agent.tracker.record_feedback(
                                    request_id=request_id,
                                    feedback="dislike",
                                )

                                st.session_state.feedback[
                                    request_id
                                ] = "dislike"

                                st.rerun()

    # ========================================================
    # New question
    # ========================================================

    question = st.chat_input(
        "Ask a question..."
    )

    if not question:
        return

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # ========================================================
    # Agent response
    # ========================================================

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Searching and thinking..."
            ):

                result = agent.ask(question)

            answer = result.get(
                "answer",
                "I couldn't generate an answer.",
            )

            tool_calls = result.get(
                "tool_calls",
                [],
            )

            # IMPORTANT
            request_id = result.get(
                "request_id"
            )

            st.markdown(answer)

            # ------------------------------------------------
            # Agent activity
            # ------------------------------------------------

            if tool_calls:

                with st.expander(
                    "🔍 Agent activity"
                ):
                    render_agent_activity(
                        tool_calls
                    )

                with st.expander(
                    "📚 Sources"
                ):
                    render_sources(
                        tool_calls
                    )

            # ------------------------------------------------
            # Save assistant message
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "tool_calls": tool_calls,
                    "request_id": request_id,
                }
            )

        except Exception as e:

            st.error(
                "Something went wrong while "
                "processing your question."
            )

            st.exception(e)