"""src/eval/judge_prompts.py

Prompt templates for each LLM-as-judge axis. Each returns strict JSON:
{"score": 1-5, "reasoning": "<short explanation>"}

Score anchors are spelled out per-axis so the judge model isn't guessing
what a "3" means -- this is what keeps LLM-judge scores reproducible
across runs and comparable across agent versions.
"""

TOOL_SELECTION_JUDGE_PROMPT = """You are auditing whether an AI agent followed its OWN tool-routing rules.

The agent's system prompt defines this routing policy:
- Use `search_internal_documentation` for company processes, coding standards, \
tools, architecture, or project specs (this is the default for anything company-related).
- Use `search_web` ONLY for general public knowledge, external tech news, current \
public events, or third-party docs not covered internally.

USER QUESTION:
{question}

TOOLS THE AGENT ACTUALLY CALLED (in order):
{tool_calls_summary}

Judge whether the tool(s) chosen -- and the ORDER/whether internal was tried first \
where relevant -- match the routing policy above, given the question. Do not judge \
answer quality, only tool choice.

Score 1-5:
5 = Correct tool(s), correct order, no unnecessary calls
4 = Correct tool(s), minor inefficiency (e.g. one redundant call) but no policy violation
3 = Defensible choice but policy is ambiguous for this question OR internal search \
skipped when it arguably should have been tried first
2 = Wrong primary tool for this question type (e.g. web search used for an internal \
company topic, or vice versa)
1 = No tool called when one was clearly needed, or tool choice actively contradicts policy

Respond with ONLY this JSON, no other text:
{{"score": <int 1-5>, "reasoning": "<one or two sentences>"}}
"""

RETRIEVAL_RELEVANCE_JUDGE_PROMPT = """You are auditing the RELEVANCE of retrieved content, \
not the final answer.

SEARCH QUERY SENT TO THE TOOL:
{query}

TOOL: {tool_name}

CONTENT RETURNED:
{tool_output}

Judge how relevant the retrieved content is to the query. Ignore whether the final \
answer used it well -- only judge whether a competent researcher would consider this \
retrieval useful for the query.

Score 1-5:
5 = Highly relevant, directly answers or strongly supports the query
4 = Mostly relevant, some tangential content mixed in
3 = Partially relevant, would need significant filtering to be useful
2 = Mostly irrelevant, only superficial keyword overlap
1 = Irrelevant or empty/error result

Respond with ONLY this JSON, no other text:
{{"score": <int 1-5>, "reasoning": "<one or two sentences>"}}
"""

GROUNDEDNESS_JUDGE_PROMPT = """You are a fact-checker. Compare the agent's final answer \
against ONLY the retrieved context below. Flag any claim in the answer that is NOT \
supported by the context.

RETRIEVED CONTEXT (everything the agent had access to):
{retrieved_context}

AGENT'S FINAL ANSWER:
{answer}

Score 1-5:
5 = Every factual claim is directly supported by the retrieved context; no fabrication
4 = Mostly grounded, one minor unsupported detail (e.g. a reasonable inference clearly \
flagged as such)
3 = Mix of grounded and unsupported claims
2 = Mostly unsupported / answer goes well beyond what context provides
1 = Contradicts the retrieved context or is fabricated wholesale (hallucination), OR \
context was empty/irrelevant but the agent answered confidently anyway instead of \
saying it couldn't find relevant information

Respond with ONLY this JSON, no other text:
{{"score": <int 1-5>, "reasoning": "<one or two sentences, name the unsupported claim if any>"}}
"""

CORRECTNESS_JUDGE_PROMPT = """You are grading an agent's answer against a KNOWN CORRECT \
answer sourced directly from the company documentation. Judge semantic correctness, not \
wording overlap -- the agent's answer can be phrased completely differently and still be \
fully correct.

USER QUESTION:
{question}

GROUND TRUTH ANSWER (from the source documentation):
{expected_output}

AGENT'S ANSWER:
{agent_answer}

Score 1-5:
5 = Fully correct, covers the key facts in the ground truth, no contradictions
4 = Correct on the main point, missing a minor supporting detail present in ground truth
3 = Partially correct -- gets some facts right but omits significant parts of the ground \
truth, or is vague where the ground truth is specific
2 = Mostly incorrect or answers a different question than what the ground truth addresses
1 = Contradicts the ground truth, or agent declined/failed to answer when the ground truth \
shows the information was available

Respond with ONLY this JSON, no other text:
{{"score": <int 1-5>, "reasoning": "<one or two sentences, name what's missing or wrong if any>"}}
"""

HELPFULNESS_JUDGE_PROMPT = """You are judging whether an answer actually helps the user, \
per the agent's own formatting rules: lead with the direct answer, be concise, use \
structure (bullets/tables) where useful, cite sources when facts came from tools.

USER QUESTION:
{question}

AGENT'S FINAL ANSWER:
{answer}

Score 1-5:
5 = Directly and completely answers the question, well-formatted, cites sources where expected
4 = Answers the question, minor formatting or completeness gaps
3 = Partially answers, or answers correctly but format/citation rules ignored
2 = Vague, evasive, or only tangentially addresses the question
1 = Does not answer the question at all, or answer is incoherent

Respond with ONLY this JSON, no other text:
{{"score": <int 1-5>, "reasoning": "<one or two sentences>"}}
"""