import re

def parse_internal_sources(
    tool_output: str,
) -> list[dict]:

    if not tool_output:
        return []

    if tool_output.startswith(
        "No relevant internal documentation found."
    ):
        return []

    sources = []

    sections = re.split(
        r"\n\n---\n\n",
        tool_output,
    )

    for section in sections:

        lines = section.splitlines()

        if len(lines) < 2:
            continue

        document_line = lines[1]

        match = re.search(
            r"Document:\s*(.*?)\s*"
            r"\(Category:\s*(.*?),\s*"
            r"Source:\s*(.*?)\)",
            document_line,
        )

        if not match:
            continue

        title = match.group(1).strip()
        category = match.group(2).strip()
        source = match.group(3).strip()

        text = "\n".join(
            lines[3:]
        ).strip()

        sources.append(
            {
                "title": title,
                "category": category,
                "source": source,
                "text": text,
            }
        )

    return sources