# PhishGuard AI

An explainable phishing-risk triage and retrieval-augmented guidance application for suspicious emails and text messages. PhishGuard combines a lightweight NLP classifier, transparent security signals, a curated phishing knowledge base, and an optional Claude-grounded RAG response layer.

> **Educational demo:** do not paste passwords, payment details, or private organisational data. The included classifier uses a deliberately small demonstration dataset and is not a production security control.

## What it does

PhishGuard answers two related questions:

1. **How risky does this message appear?** — using TF-IDF + logistic regression and visible phishing signals.
2. **What should I do next?** — using retrieval-augmented defensive guidance with traceable sources.

## Features

- FastAPI REST API with automatic OpenAPI documentation
- TF-IDF + logistic-regression phishing classification
- Explainable signals for urgency, credential requests, threats, lures, links, and attachments
- Hybrid risk score combining model probability with detected security signals
- Retrieval-augmented phishing guidance via `/api/rag`
- Curated Australian Cyber Security Centre knowledge base with source URLs
- Local TF-IDF top-k retrieval
- Optional Claude generation grounded only in retrieved evidence
- Prompt-injection-aware RAG system prompt that treats suspicious message text as untrusted content
- Deterministic retrieval fallback when no LLM credentials are configured
- SQLite analysis history using parameterised queries
- Responsive browser UI for both classification and RAG guidance
- Pydantic validation, tests, Ruff, Docker, and GitHub Actions CI

## Architecture

```text
                               ┌─ TF-IDF + Logistic Regression
Browser UI ── FastAPI ── analyse ─┤
                               └─ Security-signal rules ──> Risk score

Browser UI ── FastAPI ── RAG query ──> TF-IDF retriever ──> phishing knowledge base
                                                   │
                                                   ├─> Claude grounded generation (optional)
                                                   └─> evidence-based fallback
```

## RAG flow

1. A user asks a phishing-safety question or describes what happened.
2. The query is vectorised with the same local TF-IDF vocabulary as the curated knowledge base.
3. Cosine similarity ranks the most relevant guidance documents.
4. The top-k documents are returned as traceable evidence.
5. If `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` are configured, Claude receives only the retrieved context plus a defensive system prompt and generates a grounded answer.
6. Without LLM credentials, the app still works and returns an evidence-based retrieval fallback.

This design keeps the demo reproducible while still showing a complete retrieval-augmented generation path.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Enable Claude-grounded generation

Set your own environment variables before starting the API:

```bash
export ANTHROPIC_API_KEY="your-api-key"
export ANTHROPIC_MODEL="your-supported-model-id"
uvicorn app.main:app --reload
```

Secrets are not stored in the repository. If either variable is missing, `/api/rag` automatically uses the local retrieval fallback.

## API examples

### Analyse a message

```bash
curl -X POST http://127.0.0.1:8000/api/analyse \
  -H 'Content-Type: application/json' \
  -d '{"text":"Urgent: your account is suspended. Login now to verify your password."}'
```

### Ask the RAG assistant

```bash
curl -X POST http://127.0.0.1:8000/api/rag \
  -H 'Content-Type: application/json' \
  -d '{"query":"I entered my password into a suspicious login page. What should I do?","top_k":3}'
```

The response includes the answer, how it was generated, and the retrieved source documents with relevance scores and URLs.

### Retrieve recent analyses

```bash
curl http://127.0.0.1:8000/api/history?limit=10
```

## How the risk score works

The logistic-regression model estimates a phishing probability from unigram and bigram TF-IDF features. Rule-based detectors independently identify visible security signals. The public risk score is currently:

```text
risk score = 65% model probability + 35% capped signal score
```

This keeps the classification result easy to inspect while demonstrating an end-to-end ML inference pipeline.

## Testing

```bash
ruff check .
pytest
```

The test suite covers API validation, risk analysis, security signals, RAG retrieval ranking, and the no-API-key fallback path.

## Docker

```bash
docker build -t phishguard-ai .
docker run --rm -p 8000:8000 phishguard-ai
```

Pass the RAG environment variables to Docker only if you want optional Claude generation.

## Limitations and roadmap

- The classifier training sample is intentionally small and synthetic; no production accuracy is claimed.
- The current RAG knowledge base is deliberately compact and locally stored.
- TF-IDF retrieval is lightweight and transparent but does not capture semantic similarity as strongly as dense embeddings.
- URL reputation, sender authentication, attachment scanning, multilingual evaluation, and adversarial testing are not yet implemented.
- Planned RAG upgrades include BM25 + dense-vector retrieval, Reciprocal Rank Fusion, a larger versioned source corpus, citation-quality evaluation, retrieval metrics, and grounded-answer faithfulness testing.

## Tech stack

Python · FastAPI · scikit-learn · Anthropic SDK · SQLite · Pydantic · HTML/CSS/JavaScript · pytest · Ruff · Docker · GitHub Actions
