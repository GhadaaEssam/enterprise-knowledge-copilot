# Enterprise Knowledge Copilot

An agentic Retrieval-Augmented Generation (RAG) system for answering questions from internal engineering documentation.

The project combines **document ingestion, multiple retrieval strategies, retrieval evaluation, agentic tool calling, LLM-based answer generation, web search, LLM-as-a-Judge evaluation, user feedback, monitoring, and a Streamlit interface** into an end-to-end knowledge assistant.

---

## 🎯 Problem

Engineering organizations accumulate large amounts of internal documentation covering development practices, tools, testing, communication, processes, and technical standards.

Although this information is available, finding the right answer can be difficult because:

* Documentation is distributed across many documents.
* Users may not know where a specific piece of information is located.
* Manually searching documentation is time-consuming.
* A general-purpose LLM may not know company-specific information.
* An LLM can generate plausible answers that are not supported by the company's documentation.

The goal of **Enterprise Knowledge Copilot** is to provide a conversational interface where employees can ask questions in natural language and receive answers grounded in the company's engineering documentation.

### Why Web Search?

Not every question should be answered exclusively from internal documentation.

The system therefore also provides a **Web Search tool** for questions that require:

* General technical knowledge
* Information that may have changed recently
* Current external information
* Topics that are not covered by the company's internal documentation

The agent can therefore use the appropriate information source:

```text
                    User Question
                         │
                         ▼
                  Knowledge Agent
                    /          \
                   /            \
                  ▼              ▼
       Internal Documentation   Web Search
             Search                Search
                  \              /
                   \            /
                    ▼          ▼
                    LLM Answer
```

For company-specific questions, the internal knowledge base is the primary source. Web search provides an additional source when external or up-to-date information is required.

---

# 🏗️ Architecture

The complete system consists of two major pipelines:

1. **Knowledge ingestion and retrieval pipeline**
2. **Agentic question-answering pipeline**

```text
                    ┌──────────────────────────────┐
                    │     HMN Engineering Docs     │
                    │  https://engineering.hmn.md/ │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                         Scrape Documentation
                                   │
                                   ▼
                         Raw Markdown Files
                                   │
                                   ▼
                         Clean Markdown
                                   │
                                   ▼
                    Markdown-Aware Chunking
                                   │
                                   ▼
                         Generate Embeddings
                              (ONNX)
                                   │
                                   ▼
                         Build Vector Database
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
          Keyword Search     Vector Search      Hybrid Search
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                                   ▼
                         Retrieval Evaluation
                                   │
                                   ▼
                         Select Best Approach
                                   │
                                   ▼
                         Internal Search Tool
                                   │
                                   │
User ──► Streamlit ──► Knowledge Agent
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
             Internal Search       Web Search
                    │                    │
                    └─────────┬──────────┘
                              │
                              ▼
                              LLM
                              │
                              ▼
                         Final Answer
                              │
                 ┌────────────┼─────────────┐
                 ▼            ▼             ▼
              Sources    Agent Activity   Feedback
                                             │
                                             ▼
                                      Monitoring
                                      Dashboard
```

---

# 📥 Knowledge Ingestion Pipeline

The knowledge base is built from the HMN engineering documentation:

**Source:** https://engineering.hmn.md/

The ingestion pipeline transforms the website documentation into searchable knowledge.

## 1. Scrape Documentation

The engineering documentation is scraped from:

```text
https://engineering.hmn.md/
```
The Scrapping script is available in:

```text
src/ingestion/scraper.py
```

The result is a collection of 60 raw Markdown documents.

---

## 2. Clean Raw Markdown Files

The raw Markdown files are cleaned before being added to the knowledge base.

The cleaning process:

* Removes image Markdown such as `![](...)`
* Removes navigation elements such as `Previous` and `Next`
* Removes unnecessary empty lines
* Removes duplicate whitespace
* Preserves headings
* Preserves bullet lists
* Preserves code blocks

The Cleaning script is available in:

```text
src/ingestion/scraper.py
```

Preserving Markdown structure is important because headings, lists, and code examples often contain important semantic information for retrieval.

---

## 3. Chunk Documents

The 60 cleaned documents are divided into 580 smaller chunks using **Markdown-aware chunking**.

The goal is to create chunks that are:

* Small enough for efficient retrieval
* Large enough to preserve meaningful context
* Structured around the original Markdown content

Each chunk retains metadata such as its document, title, category, and source.

---

## 4. Generate Embeddings

Embeddings are generated using **ONNX Runtime**.

These embeddings are used by the vector retrieval implementation.

---

## 5. Build the Search Database

The processed documents and embeddings are stored in the searchable knowledge base.

Three retrieval approaches were then implemented:

```text
Clean Documents
      │
      ▼
    Chunks
      │
      ▼
Knowledge Base
      │
      ├──────────────► Keyword Search
      │
      ├──────────────► Vector Search
      │
      └──────────────► Hybrid Search
```

The three approaches were evaluated before selecting the retrieval strategy used by the final application.

---

# 🔎 Retrieval Evaluation

Rather than assuming that vector or hybrid search would perform best, three retrieval techniques were implemented and evaluated:

1. `KeywordSearchEngine`
2. `SqliteVectorSearchEngine`
3. `HybridSearchEngine`

The evaluation is available in:

```text
notebooks/retrieval_evaluation.ipynb
```

Two retrieval metrics were used.

### Hit Rate@5

Measures whether the relevant document appears within the top five retrieved results.

### MRR@5

Mean Reciprocal Rank measures how highly the relevant result appears in the top five results.

A higher MRR means relevant results tend to appear closer to the top.

---

## Retrieval Results

| Retrieval Engine         | Hit Rate@5 |      MRR@5 |
| ------------------------ | ---------: | ---------: |
| **KeywordSearchEngine**  | **0.9089** | **0.7333** |
| SqliteVectorSearchEngine |     0.7936 |     0.6210 |
| HybridSearchEngine       |     0.8934 |     0.7011 |

### Selected Retrieval Strategy

`KeywordSearchEngine` was selected for the final system because it achieved the best performance on both metrics:

```text
Hit Rate@5 = 90.89%
MRR@5      = 73.33%
```

The hybrid approach also performed strongly, but keyword search achieved the highest retrieval performance on this particular documentation dataset.

This evaluation demonstrates that the retrieval strategy was selected based on measured performance rather than assumptions about which retrieval method should work best.

---

# 🤖 Agentic RAG Pipeline

The final application uses a custom **Knowledge Agent** with LLM tool calling.

When a user asks a question, the agent determines which tool should be used.

The available tools are:

* **Internal Documentation Search**
* **Web Search**

The resulting context is then provided to the LLM for final answer generation.

The flow is:

```text
User Question
      │
      ▼
Knowledge Agent
      │
      ▼
LLM decides whether a tool is needed
      │
      ├───────────────────────┐
      │                       │
      ▼                       ▼
Internal Search           Web Search
      │                       │
      │                       │
      └───────────┬───────────┘
                  │
                  ▼
             Tool Results
                  │
                  ▼
              LLM Again
                  │
                  ▼
            Final Answer
```

The agent supports multiple iterations.

For example:

```text
Question
   ↓
Internal Search
   ↓
Retrieved Context
   ↓
LLM
   ↓
Additional Search if needed
   ↓
LLM
   ↓
Final Answer
```

A maximum iteration limit is used to prevent endless tool-calling loops.

---

# 📚 Sources and Agent Activity

The Streamlit interface exposes useful information about how the answer was generated.

### Agent Activity

Users can inspect:

* Which tools were called
* The arguments passed to each tool
* The number of retrieval iterations

### Sources

For internal documentation questions, the application displays the retrieved documentation used to generate the answer.

This makes the system more transparent and helps users verify the source of the answer.

---

# 🧪 LLM Evaluation

Retrieval evaluation answers the question:

> "Did we retrieve the right information?"

However, good retrieval does not necessarily mean that the LLM will generate a good final answer.

Therefore, the project also evaluates the **final agent answers** using an **LLM-as-a-Judge** approach.

The evaluation dataset contains **100 test cases generated from the chunked documentation**.

The test cases are based on the actual knowledge base content, allowing the generated questions and expected answers to reflect information that exists in the documentation.

The evaluation script is:

```text
src/evaluation/evaluate.py
```

The generated evaluation report is stored at:

```text
eval_data/eval_report.json
```

---

# 📊 LLM Evaluation Methodology

Two independent evaluation dimensions are used:

1. Correctness
2. Groundedness

---

## Correctness

The correctness judge compares the agent's answer against a known correct answer sourced directly from the company documentation.

The judge is explicitly instructed to evaluate **semantic correctness rather than wording overlap**.

The scoring criteria are:

```text
5 = Fully correct, covers the key facts in the ground truth, no contradictions

4 = Correct on the main point, missing a minor supporting detail

3 = Partially correct, but omits significant information or is vague

2 = Mostly incorrect or answers a different question

1 = Contradicts the ground truth or fails to answer when information was available
```

The judge returns both:

* A score from 1–5
* A short explanation identifying missing or incorrect information

---

## Groundedness

Groundedness evaluates whether the final answer is actually supported by the context available to the agent.

The judge compares:

```text
Retrieved Context
       ↓
Agent Answer
```

The judge is instructed to flag factual claims that are not supported by the retrieved context.

The scoring criteria are:

```text
5 = Every factual claim is directly supported by the context

4 = Mostly grounded with one minor unsupported detail

3 = Mix of grounded and unsupported claims

2 = Mostly unsupported or goes significantly beyond the context

1 = Contradicts the context, is fabricated, or confidently answers
    when the retrieved context is empty/irrelevant
```

This is particularly important for a RAG system because an answer can be factually correct while still being **ungrounded in the retrieved company documentation**.

---

# 📈 LLM Evaluation Results

The evaluation was run against 100 test cases.

| Metric       |         Mean | Minimum | Scored | Missing |
| ------------ | -----------: | ------: | -----: | ------: |
| Correctness  | **2.78 / 5** |       1 |     99 |       1 |
| Groundedness | **3.53 / 5** |       1 |     98 |       2 |

The missing scores were caused by **evaluation/LLM limit errors**, rather than missing test cases.

### Interpretation

The results provide a useful baseline for the system.

The groundedness score of **3.53/5** indicates that the retrieved context generally contributes meaningful support to the generated answers.

The correctness score of **2.78/5** indicates that there is still significant room for improving final answer quality.

This gives a measurable baseline for future improvements to:

* Agent instructions
* Retrieval context
* Query formulation
* Tool selection
* Answer generation
* Model selection

---

# 🖥️ Streamlit Interface

The project provides a complete interactive UI using Streamlit.

The application contains:

### 💬 Copilot

Users can ask questions in natural language.

### 🔍 Agent Activity

Shows the tools used by the agent and their arguments.

### 📚 Sources

Displays retrieved internal documentation.

### 👍 / 👎 Feedback

Users can indicate whether an answer was helpful.

### 📊 Evaluation

Displays the LLM evaluation results.

### 📈 Monitoring

Provides operational metrics and visualizations.

---

# 📈 Monitoring

The project includes a dedicated monitoring dashboard.

Monitoring is stored separately from the retrieval knowledge base.

The dashboard tracks:

* Number of requests
* Response latency
* Token usage
* Input vs output tokens
* Tool usage
* Tool latency
* Model usage
* Estimated cost
* Recent requests
* User feedback

The monitoring dashboard contains more than five charts and allows the system's operational behavior to be inspected over time.

---

# 👍 User Feedback

After receiving an answer, users can provide:

```text
👍 Helpful
👎 Not Helpful
```

The feedback is associated with the corresponding request.

This provides a feedback signal that can later be used to investigate:

* Which questions receive negative feedback
* Which answers need improvement
* Whether certain tools produce better answers
* Whether retrieval quality correlates with user satisfaction

---

# 📁 Project Structure

```text
enterprise-knowledge-copilot/
│
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
│
├── app/
│   ├── components/
│   │   ├── agent_activity.py
│   │   ├── chat.py
│   │   ├── evaluation.py
│   │   ├── monitoring.py
│   │   ├── sidebar.py
│   │   └── sources.py
│   │
│   ├── utils/
│   │   ├── agent.py
│   │   └── parsing.py
│   │
│   └── streamlit_app.py
│
├── data/
│   ├── db/
│   ├── embeddings/
│   │   └── embeddings.npy
│   ├── evaluation/
│   │   ├── ground_truth.json
│   │   └── ground_truth_augmented.json
│   ├── monitoring/
│   ├── notebooks/
│   ├── processed/
│   │   ├── chunked_documents.json
│   │   ├── cleaned_documents.json
│   │   └── hmn_engineering_docs/
│   └── raw/
│       └── hmn_engineering_docs/
│
├── eval_data/
│   ├── eval_report.json
│   ├── generations.json
│   └── ground_truth_sample.json
│
├── notebooks/
│   ├── main.ipynb
│   └── retrieval_evaluation.ipynb
│
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompt.py
│   │
│   ├── evaluation/
│   │   ├── boost_fields_tuning.py
│   │   ├── evaluate.py
│   │   ├── generate_answers.py
│   │   ├── gt_generation.py
│   │   ├── judge.py
│   │   ├── judge_prompts.py
│   │   ├── retry_failed.py
│   │   ├── sample_ground_truth.py
│   │   └── search_evaluation.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── cleaner.py
│   │   ├── embed/
│   │   ├── embedder.py
│   │   ├── embedding.py
│   │   ├── loader.py
│   │   ├── models/
│   │   ├── pipeline.py
│   │   └── scraper.py
│   │
│   ├── monitoring/
│   │   ├── database.py
│   │   ├── pricing.py
│   │   └── tracker.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── search_engines.py
│   │   ├── text_search.py
│   │   └── vector_search.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── handlers.py
│       ├── internal_search.py
│       ├── tool_registry.py
│       └── web_search.py
└──
```

---

# ⚙️ Technology Stack

* **Python 3.12+**
* **Streamlit** — user interface
* **SQLite** — knowledge base and monitoring storage
* **ONNX Runtime** — embedding generation
* **minsearch / SQLite search** — retrieval implementations
* **Groq** — LLM API
* **OpenAI-compatible LLM interface** — agent interaction
* **DDGS** — web search
* **BeautifulSoup / Crawl4AI** — documentation ingestion
* **Markdownify** — HTML to Markdown conversion
* **uv** — dependency and environment management
* **Docker / Docker Compose** — containerization

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd enterprise-knowledge-copilot
```

## 2. Install dependencies

The project uses `uv`.

```bash
uv sync
```

The repository contains `uv.lock`, which records the resolved dependency versions.

---

# 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Never commit API keys to Git.

A `.env.example` file should contain:

```env
GROQ_API_KEY=
```

---

# 🗃️ Knowledge Base

The knowledge base is generated from the HMN engineering documentation:

```text
https://engineering.hmn.md/
```

The ingestion pipeline produces the searchable knowledge base used by the retrieval engines.

The retrieval database and monitoring database are kept separate.

---

# ▶️ Run the Application

Run Streamlit locally:

```bash
uv run streamlit run app/streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

---

# 🐳 Docker

The complete application can also be run using Docker Compose.

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

Or run in the background:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

The application will be available at:

```text
http://localhost:8501
```

---

# 🔬 Reproducing the Experiments

## Retrieval Evaluation

The retrieval experiments can be found in:

```text
notebooks/retrieval_evaluation.ipynb
```

The notebook evaluates:

```text
Keyword Search
Vector Search
Hybrid Search
```

using:

```text
Hit Rate@5
MRR@5
```

The best-performing approach is then selected for the final application.

---

## LLM Evaluation

Run the LLM evaluation using:

```text
src/evaluation/evaluate.py
```

The evaluation produces:

```text
eval_data/eval_report.json
```

The Streamlit evaluation page reads this report and displays:

* Number of test cases
* Average correctness
* Average groundedness
* Individual evaluation results
* Judge reasoning

---

# 🚧 Future Improvements

Several improvements can be added to further enhance the system.

### Automated Ingestion

The current ingestion process can be extended into a fully automated pipeline using orchestration tools such as Airflow, Prefect, or Kestra.

### Query Rewriting

A query rewriting stage could transform short or ambiguous questions into more retrieval-friendly queries.

### Document Re-ranking

A re-ranking stage could be added after the initial retrieval:

```text
Query
  ↓
Initial Retrieval
  ↓
Top N Candidates
  ↓
Re-ranker
  ↓
Top K Context
  ↓
LLM
```

### Better Retrieval

Additional experiments could include:

* BM25
* Improved embedding models
* Semantic chunking
* Query expansion
* Metadata-aware retrieval
* Cross-encoder re-ranking

### LLM Evaluation

Future experiments could compare different:

* LLM models
* Agent prompts
* Retrieval configurations
* Context sizes
* Answer-generation strategies

The best configuration could then be selected using correctness and groundedness as evaluation criteria.

---

# 🎯 Project Summary

Enterprise Knowledge Copilot is an end-to-end agentic RAG system designed to make internal engineering documentation easier to access through natural-language interaction.

The project follows an evidence-based development process:

```text
Engineering Documentation
          │
          ▼
       Scraping
          │
          ▼
    Markdown Cleaning
          │
          ▼
   Markdown Chunking
          │
          ▼
    ONNX Embeddings
          │
          ▼
     Knowledge Base
          │
          ▼
 ┌─────────────────────┐
 │ Evaluate Retrieval  │
 │                     │
 │ Keyword             │
 │ Vector              │
 │ Hybrid              │
 └──────────┬──────────┘
            │
            ▼
    Select Best Retriever
            │
            ▼
     Internal Search Tool
            │
            ├──────────────┐
            │              │
            ▼              ▼
     Internal Docs     Web Search
            │              │
            └──────┬───────┘
                   ▼
              Knowledge Agent
                   │
                   ▼
                  LLM
                   │
                   ▼
             Final Answer
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Sources  Feedback  Monitoring
                           │
                           ▼
                     Dashboard
```

The final system therefore goes beyond a basic RAG implementation by combining **retrieval experimentation, agentic tool use, external web search, answer evaluation, user feedback, monitoring, and containerized deployment** into a single application.