import streamlit as st


def render_agent_activity(
    tool_calls: list[dict],
):

    if not tool_calls:

        st.caption(
            "No tools were used."
        )

        return

    for i, tool_call in enumerate(
        tool_calls,
        1,
    ):

        name = tool_call.get(
            "name",
            "unknown_tool",
        )

        iteration = tool_call.get(
            "iteration",
            "?",
        )

        arguments = (
            tool_call.get(
                "arguments"
            )
            or {}
        )

        if name == "search_internal_documentation":

            icon = "📚"
            label = "Internal Documentation"

        elif name == "search_web":

            icon = "🌐"
            label = "Web Search"

        else:

            icon = "🔧"
            label = name

        st.markdown(
            f"**{icon} {label}** "
            f"· Iteration {iteration}"
        )

        query = arguments.get(
            "query"
        )

        if query:

            st.code(
                query,
                language=None,
            )