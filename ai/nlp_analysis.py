from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


# Prototype bilingual keyword dictionaries
FEAR_WORDS = [
    "fear", "afraid", "scared", "terrified", "threat",
    "unsafe", "danger", "darr", "dar", "khauf",
    "dhamki", "khatra", "asurakshit"
]

STRESS_WORDS = [
    "stress", "stressed", "pressure", "overwhelmed",
    "tension", "difficult", "hard", "worried",
    "pareshan", "tension", "tanav", "mushkil",
    "pressure", "thak", "neend nahi"
]

NEGATIVE_WORDS = [
    "sad", "hopeless", "helpless", "alone", "cry",
    "upset", "broken", "worried", "udaas",
    "akeli", "bebas", "rona", "pareshan"
]

ANXIETY_WORDS = [
    "anxiety", "anxious", "panic", "panicked", "restless",
    "uneasy", "nervous", "worry", "worried",
    "ghabrahat", "ghabrahat ho rahi", "bechain",
    "ghabra", "chinta", "ashant", "ghabrahat"
]


def keyword_score(text, keywords):
    text = text.lower()

    matches = []
    for word in keywords:
        if word in text:
            matches.append(word)

    # Cap the score at 100
    score = min(len(matches) * 25, 100)

    return score, matches


def analyze_text(text):
    if not text:
        return {
            "fear_score": 0,
            "stress_score": 0,
            "negative_emotion_score": 0,
            "sentiment": 0,
            "matched_indicators": []
        }

    text = text.strip()

    # English sentiment analysis
    sentiment_result = analyzer.polarity_scores(text)
    sentiment = sentiment_result["compound"]

    fear_score, fear_matches = keyword_score(text, FEAR_WORDS)
    stress_score, stress_matches = keyword_score(text, STRESS_WORDS)
    negative_score, negative_matches = keyword_score(text, NEGATIVE_WORDS)
    anxiety_score, anxiety_matches = keyword_score(
    text, ANXIETY_WORDS
)

    all_matches = (
        fear_matches +
        stress_matches +
        negative_matches +
        anxiety_matches
    )

    return {
        "fear_score": fear_score,
        "stress_score": stress_score,
        "anxiety_score": anxiety_score,
        "negative_emotion_score": negative_score,
        "sentiment": sentiment,
        "matched_indicators": all_matches
    }
if __name__ == "__main__":
    text = "Mujhe baar-baar court jaana bahut difficult lag raha hai. Mujhe dar bhi lagta hai."

    result = analyze_text(text)

    print(result)