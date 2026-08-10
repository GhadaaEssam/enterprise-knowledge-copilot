import streamlit as st

from app.utils.parsing import parse_internal_sources

def render_sources(
    tool_calls: list[dict],
):

    internal_calls = [
        tc
        for tc in tool_calls
        if tc.get("name")
        == "search_internal_documentation"
    ]

    if not internal_calls:

        st.caption(
            "No internal documentation sources "
            "were retrieved."
        )

        return

    for tool_call in internal_calls:

        sources = parse_internal_sources(
            str(
                tool_call.get(
                    "output",
                    "",
                )
            )
        )

        for source in sources:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**📄 {source['title']}**"
                )

                st.caption(
                    f"{source['source']} · "
                    f"{source['category']}"
                )

                text = source["text"]

                if len(text) > 500:
                    text = (
                        text[:500]
                        + "..."
                    )

                st.write(text)