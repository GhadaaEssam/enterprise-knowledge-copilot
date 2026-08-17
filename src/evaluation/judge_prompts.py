"""src/eval/judge_prompts.py

Prompt templates for each LLM-as-judge axis. Each returns strict JSON:
{"score": 1-5, "reasoning": "<short explanation>"}

Score anchors are spelled out per-axis so the judge model isn't guessing
what a "3" means -- this is what keeps LLM-judge scores reproducible
across runs and comparable across agent versions.
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

CONTEXT_RELEVANCE_JUDGE_PROMPT = """
You are evaluating the relevance of retrieved context for an enterprise
knowledge assistant.

Determine whether the retrieved context is actually useful for answering
the user's question.

USER QUESTION:

{question}

RETRIEVED CONTEXT:

{retrieved_context}

Score 1-5:

5 = The retrieved context is directly relevant and contains the information
    needed to answer the question.

4 = Mostly relevant, with only a small amount of irrelevant information or
    minor missing context.

3 = Some relevant information is present, but substantial irrelevant or
    missing information remains.

2 = Mostly irrelevant context; only a small portion is potentially useful.

1 = The context is empty, irrelevant, or does not help answer the question.

Respond with ONLY this JSON, no other text:

{{"score": <int 1-5>, "reasoning": "<one or two sentences explaining why the context is or is not relevant>"}}
"""