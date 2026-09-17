from app.classifier import PhishingClassifier


def test_classifier_scores_phishing_above_normal_message():
    classifier = PhishingClassifier()

    phishing_score, _, phishing_signals = classifier.analyse(
        "Final warning: login now and provide your password at http://bit.ly/account"
    )
    normal_score, _, normal_signals = classifier.analyse(
        "The project meeting is confirmed for tomorrow at ten in the usual room"
    )

    assert phishing_score > normal_score
    assert len(phishing_signals) > len(normal_signals)


def test_score_stays_within_public_api_range():
    classifier = PhishingClassifier()
    score, probability, _ = classifier.analyse("urgent password login refund gift card http://x.test")

    assert 0 <= score <= 100
    assert 0 <= probability <= 1

