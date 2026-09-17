import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TRAINING_SAMPLES: list[tuple[str, int]] = [
    ("Your account is suspended. Verify your password immediately at this link", 1),
    ("Urgent: unusual sign-in detected. Confirm your identity now", 1),
    ("You won a gift card. Click here and enter your banking details", 1),
    ("Invoice overdue. Open the attached document and enable macros", 1),
    ("CEO request: buy gift cards today and send me the codes", 1),
    ("Your mailbox storage is full. Login now to avoid deletion", 1),
    ("Final warning: tax refund expires today. Submit card details", 1),
    ("Security alert: reset your account at http://bit.ly/verify-now", 1),
    ("Package held. Pay a small redelivery fee using this link", 1),
    ("Payroll update required. Reply with your password and employee number", 1),
    ("Can we move tomorrow's project meeting to 10 am?", 0),
    ("Please review the attached agenda before our weekly meeting", 0),
    ("Your library book is due next Tuesday", 0),
    ("Thanks for submitting the report. I added comments in the document", 0),
    ("The deployment completed successfully and all checks passed", 0),
    ("Here are the lecture slides and tutorial exercises for this week", 0),
    ("Your order has shipped and will arrive on Friday", 0),
    ("Reminder: complete your timesheet before the end of the week", 0),
    ("The team lunch is booked for noon at the campus cafe", 0),
    ("Please use the official portal to view your enrolment details", 0),
]


@dataclass(frozen=True)
class DetectedSignal:
    label: str
    detail: str
    severity: str
    weight: int


SIGNAL_PATTERNS: list[tuple[str, str, str, int, str]] = [
    (
        r"\b(urgent|immediately|final warning|act now|today only)\b",
        "Urgency language",
        "The message pressures the reader to act quickly.",
        12,
        "medium",
    ),
    (
        r"\b(password|pin|cvv|banking details|card details|login)\b",
        "Sensitive information",
        "It requests or references credentials or financial information.",
        22,
        "high",
    ),
    (
        r"\b(suspended|locked|unusual sign-in|avoid deletion|expires)\b",
        "Threat or consequence",
        "It threatens account loss or another negative consequence.",
        16,
        "high",
    ),
    (
        r"\b(gift card|prize|won|refund)\b",
        "Financial lure",
        "It uses a reward, refund, or unusual payment request.",
        18,
        "high",
    ),
    (
        r"https?://|www\.|\bbit\.ly/",
        "External link",
        "It contains a link that should be independently verified.",
        10,
        "medium",
    ),
    (
        r"\b(enable macros|download attachment|open the attached)\b",
        "Risky attachment instruction",
        "It asks the reader to open active content or an attachment.",
        20,
        "high",
    ),
]


class PhishingClassifier:
    """Hybrid classifier combining ML probability with transparent security signals."""

    def __init__(self) -> None:
        texts, labels = zip(*TRAINING_SAMPLES, strict=True)
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
                ("model", LogisticRegression(random_state=42, max_iter=1_000)),
            ]
        )
        self.pipeline.fit(texts, labels)

    def analyse(self, text: str) -> tuple[int, float, list[DetectedSignal]]:
        probability = float(self.pipeline.predict_proba([text])[0][1])
        signals = self._detect_signals(text)
        heuristic_score = min(sum(signal.weight for signal in signals), 100)
        combined_score = round((probability * 65) + (heuristic_score * 0.35))
        return max(0, min(combined_score, 100)), probability, signals

    @staticmethod
    def _detect_signals(text: str) -> list[DetectedSignal]:
        signals: list[DetectedSignal] = []
        for pattern, label, detail, weight, severity in SIGNAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                signals.append(DetectedSignal(label, detail, severity, weight))
        return signals
