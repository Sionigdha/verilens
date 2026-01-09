from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from textblob import TextBlob
import re

# Small sample training data (for MVP demo)
texts = [
    "Breaking shocking news you won't believe",
    "Official government report released today",
    "Miracle cure doctors don't want you to know",
    "Peer reviewed scientific study published"
]

labels = [1, 0, 1, 0]  # 1 = higher misinformation risk

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

def analyze_text(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    risk_score = int(prob * 100)

    # Calculate sentiment FIRST
    sentiment = TextBlob(text).sentiment.polarity

    # Heuristic adjustment for neutral / institutional tone
    if risk_score < 50 and abs(sentiment) < 0.2:
        risk_score = max(5, risk_score - 30)

    # ---- FIX 2: Reduce risk for authoritative institutions ----
    if has_authoritative_entity(text):
        risk_score = max(0, risk_score - 20)

    # Clamp score to valid range
    risk_score = max(0, min(100, risk_score))

    tone = "Emotional" if abs(sentiment) > 0.4 else "Neutral"

    return risk_score, tone

def analyze_claims(text):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    results = []

    for s in sentences:
        risk, tone = analyze_text(s)
        results.append({
            "claim": s,
            "risk": risk,
            "tone": tone
        })

    # Sort by highest risk
    results = sorted(results, key=lambda x: x["risk"], reverse=True)
    return results
def virality_risk(text):
    trigger_words = [
        "shocking", "breaking", "secret", "exposed",
        "miracle", "you won't believe", "truth revealed"
    ]

    score = 0
    lower_text = text.lower()

    for word in trigger_words:
        if word in lower_text:
            score += 1

    punctuation_score = text.count("!") + text.count("?")
    sentiment = abs(TextBlob(text).sentiment.polarity)

    if score >= 2 or sentiment > 0.5 or punctuation_score > 3:
        return "High"
    elif score == 1 or sentiment > 0.3:
        return "Medium"
    else:
        return "Low"
def explain_score(text, risk):
    reasons = []
    text_lower = text.lower()
    word_count = len(text.split())

    # --- Signal 1: Sensational / Clickbait Language ---
    SENSATIONAL_WORDS = [
        "breaking", "shocking", "miracle", "exposed",
        "you won’t believe", "secret", "revealed"
    ]

    if any(word in text_lower for word in SENSATIONAL_WORDS):
        reasons.append(
            "Uses sensational or clickbait-style language commonly associated with misinformation spread."
        )

    # --- Signal 2: Institutional Attribution ---
    INSTITUTIONAL_KEYWORDS = [
        "reserve bank", "ministry", "government",
        "central bank", "announced", "reported by",
        "according to", "official", "policy"
    ]

    if not any(word in text_lower for word in INSTITUTIONAL_KEYWORDS):
        reasons.append(
            "Does not reference a clearly identifiable institution or authoritative source."
        )

    # --- Signal 3: Emotional Tone ---
    EMOTIONAL_WORDS = ["outrage", "fear", "anger", "panic", "hate", "destroy"]

    if any(word in text_lower for word in EMOTIONAL_WORDS):
        reasons.append(
            "Contains emotionally charged language that may influence reader reaction."
        )

    # --- Signal 4: Limited Context ---
    if word_count < 25:
        reasons.append(
            "Very short content length provides limited context for reliable interpretation."
        )

    # --- Positive Signal (important for low-risk cases) ---
    if risk < 35 and len(reasons) == 0:
        reasons.append(
            "Language appears neutral and informational, with no strong misinformation indicators detected."
        )

    return reasons


def confidence_band(risk, signals_count):
    if signals_count >= 3:
        return "High", "±8%"
    elif signals_count == 2:
        return "Medium", "±12%"
    else:
        return "Low", "±18%"


def recommended_action(risk, mode):
    if mode.startswith("High-Stakes"):
        if risk >= 50:
            return [
                "Delay publication until verification",
                "Cross-check with trusted institutional sources",
                "Flag for editorial or expert review"
            ]
        else:
            return ["Proceed with caution and source attribution"]
    else:
        if risk >= 70:
            return ["Avoid sharing until verified", "Consult trusted news sources"]
        elif risk >= 40:
            return ["Verify key claims before sharing"]
        else:
            return ["No immediate action required"]
def fact_check_assist(text):
    # Split text into potential claims
    claims = [s.strip() for s in text.split('.') if len(s.strip()) > 20]

    needs_verification = []
    trigger_words = ["claim", "reveals", "secret", "miracle", "hiding", "exposed"]

    for c in claims:
        if any(word in c.lower() for word in trigger_words):
            needs_verification.append(c)

    if needs_verification:
        sources = [
            "World Health Organization (WHO)",
            "Peer-reviewed academic journals",
            "Official government or institutional publications"
        ]
        status = "No supporting institutional references detected"
    else:
        sources = ["Official institutional sources cited"]
        status = "Appears to reference institutional reporting"

    return needs_verification, sources, status

AUTHORITATIVE_ENTITIES = [
    "reserve bank", "central bank", "ministry",
    "government", "authority", "commission",
    "department", "court", "supreme court"
]

def has_authoritative_entity(text):
    text_lower = text.lower()
    return any(entity in text_lower for entity in AUTHORITATIVE_ENTITIES)
