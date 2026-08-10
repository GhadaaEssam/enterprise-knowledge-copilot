INSTRUCTIONS = """
You are an AI Engineering Knowledge Assistant.

Your role is to answer employees' questions using the provided internal engineering documentation.

Instructions:
- Base your answer ONLY on the provided context.
- If the answer is not contained in the context, say:
  "I couldn't find this information in the internal documentation."
- Do not make up policies, processes, or technical details.
- If multiple documents provide relevant information, combine them into one coherent answer.
- Use bullet points when appropriate.
- Keep the answer concise but complete.
- At the end of the answer, list the document titles used as sources.
"""

PROMPT_TEMPLATE = """
You are answering an employee's question.

QUESTION:
{question}

INTERNAL DOCUMENTATION

{context}

Provide a clear answer.

If the documentation does not contain enough information, explicitly say so.

Include the document titles you used.
""".strip()

class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model="llama-3.1-8b-instant"
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    def build_context(self, search_results: list) -> str:
        sections = []
        for doc in search_results:
            title = doc.get("title", "Untitled")
            category = doc.get("category", "N/A")
            source = doc.get("source", "N/A")
            text = doc.get("text", "")

            sections.append(
                f"Document: {title}\nCategory: {category}\nSource: {source}\n\n{text}"
            )

        return "\n\n---\n\n".join(sections)

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def generate_response(self, prompt: str) -> str:
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response.output_text

    def ask(self, query: str, num_results: int = 5) -> str:
        search_results = self.search_engine.search(query, num_results=num_results)
        prompt = self.build_prompt(query, search_results)
        return self.generate_response(prompt)