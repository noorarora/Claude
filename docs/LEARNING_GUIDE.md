# PhishGuard AI Learning Guide

Use this guide to understand the project well enough to run it, change it, and explain every design choice in an interview.

## 1. The project in one sentence

PhishGuard AI is a full-stack web application that accepts a suspicious message, estimates its phishing risk with a text-classification model, explains visible warning signs, and stores a local history of analyses.

## 2. The user journey

1. A user pastes a suspicious message into the browser.
2. JavaScript sends the text as JSON to `POST /api/analyse`.
3. Pydantic checks that the text is between 10 and 10,000 characters.
4. The classifier calculates an ML probability and finds rule-based warning signals.
5. FastAPI combines the results into a risk score and recommendation.
6. The backend saves the analysis to SQLite using a parameterised query.
7. The API returns JSON and the browser renders the score, verdict, signals, and advice.

## 3. Repository map

```text
app/
├── main.py          HTTP routes and application lifecycle
├── schemas.py       Request and response data contracts
├── classifier.py    ML model, training examples, and explainable signals
├── database.py      SQLite connection and queries
└── static/
    ├── index.html   Accessible page structure
    ├── styles.css   Responsive visual design
    └── app.js       Browser interactions and API calls
tests/               Unit and end-to-end API tests
.github/workflows/   Automated GitHub quality checks
Dockerfile           Reproducible application container
```

## 4. Backend walkthrough

### `app/main.py`

`FastAPI(...)` creates the web application. The title, description, and version also appear in the automatically generated `/docs` page.

The `lifespan` function runs when the application starts. It calls `initialise_database()` before accepting traffic, which guarantees that the required table exists.

`app.mount("/static", ...)` makes the CSS and JavaScript files available to the browser. The root route returns `index.html`.

`POST /api/analyse` is the main use case. FastAPI converts the JSON body into an `AnalysisRequest`. Invalid requests are rejected before the route logic runs. The route calls the classifier, maps the numeric score to a verdict, saves the result, and returns an `AnalysisResponse`.

`GET /api/history` accepts a validated `limit` between 1 and 50. It returns only a short message preview rather than the full stored message.

### `app/schemas.py`

Pydantic models are data contracts:

- `AnalysisRequest` describes what the client must send.
- `Signal` describes one human-readable warning sign.
- `AnalysisResponse` describes the complete API result.
- `HistoryItem` describes the smaller record returned in history.

The `Field` constraints are important. They keep the API's behaviour predictable and prevent an empty or extremely large message from reaching the classifier.

### `app/classifier.py`

The demonstration training set contains `(message, label)` pairs. Label `1` means phishing-like and label `0` means normal. The README explicitly says this is a small synthetic dataset, so the project does not pretend to have production accuracy.

`TfidfVectorizer` converts text into numeric features. TF-IDF gives a word or two-word phrase more weight when it is important in one message but not common across every message.

`ngram_range=(1, 2)` means the vectorizer uses both individual words and two-word phrases. This helps distinguish phrases such as “gift card” and “verify account”.

`LogisticRegression` learns weights for those features and returns a probability between zero and one. `random_state=42` makes relevant training behaviour reproducible, and `max_iter=1_000` gives the optimiser enough iterations to converge.

The rule list is separate from the ML model. Each regular expression detects a visible pattern such as urgency, password requests, threats, financial lures, links, or risky attachment instructions. Each detected pattern becomes an explanation shown to the user.

The final score uses:

```text
65% × ML phishing probability + 35% × rule-based signal score
```

This is a product choice rather than a scientifically calibrated formula. It demonstrates how a probabilistic model and deterministic security knowledge can work together. A production version should tune and calibrate the formula on a held-out dataset.

### `app/database.py`

SQLite provides a simple persistent database without requiring a separate server.

`database_path()` reads `PHISHGUARD_DATABASE` when it is set. Tests use this to create a temporary database and avoid changing development data.

The `connection()` context manager opens the connection, makes rows accessible by column name, commits successful work, and always closes the connection.

Every SQL statement uses `?` placeholders. Values are passed separately, which prevents user text from being interpreted as SQL code.

## 5. Frontend walkthrough

### `index.html`

The HTML contains semantic elements such as `header`, `main`, `section`, `form`, and `footer`. The textarea has a real label, and the result panel uses `aria-live="polite"` so assistive technology can announce updated results.

No frontend framework is required for this MVP. That keeps the dependency surface small while still demonstrating a complete client–server workflow.

### `app.js`

The submit handler calls `event.preventDefault()` so the browser does not reload the page. It sends JSON with `fetch`, waits for the response, and renders the result.

`escapeHtml()` places untrusted text into `textContent` before using the resulting HTML. This prevents analysed message content and server-provided strings from injecting executable markup into the page.

The `try/catch/finally` block separates three responsibilities:

- `try`: perform the request and render success;
- `catch`: show a useful error;
- `finally`: restore the button even when the request fails.

### `styles.css`

CSS custom properties in `:root` define the reusable design tokens. Grid lays out the input and result panels. The media query changes the two-column layout into one column below 800 pixels, making the interface usable on smaller screens.

## 6. Tests and automation

`test_classifier.py` checks behaviour rather than an invented accuracy number. A clearly malicious message must score higher and produce more signals than a normal message.

`test_api.py` checks health, validation, analysis output, and database history through the public HTTP interface. The temporary database fixture keeps tests isolated and repeatable.

GitHub Actions installs the development dependencies, runs Ruff, and runs pytest after every push and pull request. A failed quality check becomes visible before changes are merged.

The Dockerfile starts from a small Python image, installs only runtime dependencies, copies the application, and starts Uvicorn on port 8000. This makes the application run consistently across different machines.

## 7. Important engineering decisions

| Decision | Reason | Trade-off |
|---|---|---|
| FastAPI | Validation, type hints, and automatic API docs | Smaller ecosystem than some older frameworks |
| Logistic regression | Fast, interpretable baseline for sparse text features | Cannot understand context like a transformer |
| Hybrid score | Adds transparent reasons to an ML probability | Formula requires real calibration before production |
| SQLite | Zero-setup persistence for an MVP | Not ideal for many concurrent production users |
| Vanilla JavaScript | Simple deployment and low dependency count | More manual UI state management as the app grows |
| Parameterised SQL | Protects queries from SQL injection | Does not address every application-security concern |

## 8. What to say in an interview

### Thirty-second explanation

“I built PhishGuard AI to turn a notebook-style NLP model into a usable software product. A FastAPI backend validates suspicious messages, combines a TF-IDF logistic-regression probability with transparent phishing signals, stores results in SQLite, and serves a responsive browser interface. I added parameterised queries, API and classifier tests, Docker, and GitHub Actions. I deliberately label the current dataset as a demonstration set and describe the evaluation work needed before production.”

### Why not claim high accuracy?

The bundled data is small and synthetic. Reporting a high test accuracy on it would be misleading because similar phrases appear throughout the tiny dataset. A credible evaluation requires a larger versioned dataset, a leakage-safe split, precision, recall, F1, confusion matrices, calibration analysis, and testing on newer phishing campaigns.

### What would you build next?

1. Move labelled data into versioned files with provenance and licensing notes.
2. Add a separate training pipeline and save a versioned model artifact.
3. Evaluate false positives and false negatives on a held-out test set.
4. Calibrate probabilities and choose thresholds based on security costs.
5. Add authentication, PostgreSQL, rate limiting, structured logs, and privacy controls.
6. Deploy a public demo using only synthetic example messages.

## 9. Practice tasks

Complete these yourself to turn understanding into evidence:

1. Add a new “impersonation” rule with a test.
2. Add an endpoint that deletes all locally stored history.
3. Move the training examples into a CSV file and load them safely.
4. Add a confusion-matrix evaluation script using a separate test dataset.
5. Explain why a false negative may be more costly than a false positive in phishing detection.

