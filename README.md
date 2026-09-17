# PhishGuard AI

An explainable phishing-risk triage application that turns suspicious emails and text messages into an actionable risk score. The project combines a lightweight NLP classifier with transparent rule-based signals, then records recent analyses in a local SQLite audit trail.

> **Educational demo:** do not paste passwords, payment details, or private organisational data. The current model uses a deliberately small in-repository demonstration dataset and is not a production security control.

## Why this project exists

Many phishing classifiers return only a label. PhishGuard instead answers three questions:

1. How risky does this message appear?
2. Which observable signals contributed to that result?
3. What should the reader do next?

## Features

- FastAPI REST API with automatic OpenAPI documentation
- TF-IDF + logistic-regression text classification
- Explainable security signals for urgency, credential requests, threats, lures, links, and attachments
- Hybrid risk score combining model probability with detected signals
- SQLite history using parameterised queries
- Responsive, accessible browser interface with no frontend build step
- Pydantic validation, unit/API tests, linting, Docker, and GitHub Actions CI

## Architecture

```text
Browser UI → FastAPI endpoints → Hybrid classifier → SQLite history
                              ↘ TF-IDF + Logistic Regression
                              ↘ Regex security signals
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Test and lint

```bash
ruff check .
pytest
```

## Run with Docker

```bash
docker build -t phishguard-ai .
docker run --rm -p 8000:8000 phishguard-ai
```

## API examples

### Analyse a message

```bash
curl -X POST http://127.0.0.1:8000/api/analyse \
  -H 'Content-Type: application/json' \
  -d '{"text":"Urgent: your account is suspended. Login now to verify your password."}'
```

### Retrieve recent analyses

```bash
curl http://127.0.0.1:8000/api/history?limit=10
```

## How the score works

The logistic-regression model estimates a phishing probability from unigram and bigram TF-IDF features. Rule-based detectors independently identify visible security signals. The public risk score is currently:

```text
risk score = 65% model probability + 35% capped signal score
```

This hybrid approach keeps the result easy to inspect while still demonstrating an end-to-end ML inference pipeline.

## Honest limitations and roadmap

- The included training sample is intentionally small and synthetic; no production accuracy is claimed.
- URL reputation, attachment scanning, sender authentication, multilingual evaluation, and adversarial testing are not yet implemented.
- The next milestone is a versioned public dataset, train/validation/test evaluation, calibrated probabilities, authentication, PostgreSQL, and cloud deployment.

## Tech stack

Python · FastAPI · scikit-learn · SQLite · Pydantic · HTML/CSS/JavaScript · pytest · Ruff · Docker · GitHub Actions

