# Security signal reference

PhishGuard AI combines a lightweight text classifier with transparent rule-based indicators. The signal layer is intentionally easy to inspect so a reviewer can see why a message received additional risk weight.

| Signal | Weight | Severity | What it looks for |
| --- | ---: | --- | --- |
| Urgency language | 12 | Medium | Pressure such as “urgent”, “immediately”, or “final warning” |
| Sensitive information | 22 | High | Passwords, PINs, CVVs, banking/card details, or login requests |
| One-time code request | 22 | High | Requests to send, reply with, share, or provide OTP/MFA/verification codes |
| Threat or consequence | 16 | High | Suspensions, locked accounts, unusual sign-ins, expiry, or deletion threats |
| Financial lure | 18 | High | Gift cards, prizes, winnings, or refunds |
| External link | 10 | Medium | HTTP/HTTPS URLs, www links, or bit.ly links |
| Risky attachment instruction | 20 | High | Instructions to open attachments, download content, or enable macros |

## Scoring

Detected signal weights are summed and capped at 100. The public risk score combines that heuristic score with the logistic-regression phishing probability:

```text
risk score = 65% model probability + 35% capped signal score
```

This means a rule can raise the score while the machine-learning model still contributes most of the final result.

## Design notes

- Signals are evidence indicators, not proof that a message is malicious.
- Matching is case-insensitive.
- The one-time-code rule requires a disclosure-style action near the code phrase, helping avoid flagging every legitimate mention of a verification code.
- Link detection does not perform reputation checks or visit URLs.
- The current signal catalogue is deliberately small and suitable for an educational prototype rather than production security enforcement.

## Regression testing

`tests/test_security_signals.py` covers multi-signal credential requests, legitimate verification-code wording, and high-severity attachment instructions. These tests complement the broader classifier tests and make future rule changes safer.
