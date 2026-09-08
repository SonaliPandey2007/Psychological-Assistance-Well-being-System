from ai.nlp_analysis import analyze_text
from ai.behaviour_analysis import calculate_behaviour_score


def calculate_ddi(
    fear_score,
    stress_score,
    anxiety_score,
    negative_emotion_score,
    mood_score,
    safety_score,
    self_report_stress,
    behaviour_score
):
    """
    Calculate PAWS Dynamic Distress Index (DDI).

    DDI is a prototype screening indicator from 0-100.
    It is NOT a clinical diagnosis.
    """

    # Convert self-reported scores (1-10)
    # into 0-100 concern scores

    mood_concern = 100 - (mood_score * 10)
    safety_concern = 100 - (safety_score * 10)
    stress_concern = self_report_stress * 10

    # Combined self-report signal
    self_report_score = (
        mood_concern +
        safety_concern +
        stress_concern
    ) / 3

    # Weighted Dynamic Distress Index
    # Total weight = 1.00
    ddi = (
        fear_score * 0.18 +
        stress_score * 0.18 +
        anxiety_score * 0.12 +
        negative_emotion_score * 0.12 +
        self_report_score * 0.30 +
        behaviour_score * 0.10
    )

    # Keep score between 0 and 100
    ddi = max(0, min(100, ddi))

    # Determine risk level
    if ddi <= 50:
        risk_level = "LOW"
    elif ddi <= 70:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    return {
        "distress_index": round(ddi, 2),
        "risk_level": risk_level,
        "self_report_score": round(self_report_score, 2)
    }


def calculate_emotional_change(
    current_negative_score,
    previous_scores=None
):
    """
    Detect change in negative-emotion indicators over time.

    This is a prototype screening indicator,
    not a clinical assessment.
    """

    current_negative_score = float(
        current_negative_score or 0
    )

    if not previous_scores:
        return {
            "change": 0,
            "direction": "NO_BASELINE"
        }

    previous_average = sum(
        float(score)
        for score in previous_scores
    ) / len(previous_scores)

    change = current_negative_score - previous_average

    if change >= 10:
        direction = "INCREASING"

    elif change <= -10:
        direction = "DECREASING"

    else:
        direction = "STABLE"

    return {
        "previous_average": round(previous_average, 2),
        "current_score": round(current_negative_score, 2),
        "change": round(change, 2),
        "direction": direction
    }


def generate_explanation(
    nlp_result,
    behaviour_score,
    ddi_result,
    emotional_change=None
):
    """
    Generate human-readable reasons behind the DDI.

    This provides explainability for counsellor review.
    It does NOT provide a medical diagnosis.
    """

    reasons = []

    # Fear
    if nlp_result.get("fear_score", 0) >= 25:
        reasons.append(
            "Fear-related language detected"
        )

    # Stress
    if nlp_result.get("stress_score", 0) >= 25:
        reasons.append(
            "Stress-related language detected"
        )

    # Anxiety
    if nlp_result.get("anxiety_score", 0) >= 25:
        reasons.append(
            "Anxiety-related language detected"
        )

    # Negative emotion
    if nlp_result.get("negative_emotion_score", 0) >= 25:
        reasons.append(
            "Negative emotional indicators detected"
        )

    # Behaviour
    if behaviour_score >= 60:
        reasons.append(
            "Check-in engagement is low"
        )

    # Emotional change
    if emotional_change:
        if emotional_change.get("direction") == "INCREASING":
            reasons.append(
                "Negative emotional indicators increased"
            )

    # Fallback
    if not reasons:
        reasons.append(
            "No major distress indicators detected"
        )

    return {
        "summary": (
            f"DDI is "
            f"{ddi_result['distress_index']} "
            f"({ddi_result['risk_level']})"
        ),
        "reasons": reasons,
        "matched_indicators": nlp_result.get(
            "matched_indicators",
            []
        )
    }


def analyze_checkin(
    text,
    mood_score,
    safety_score,
    self_report_stress,
    current_engagement,
    previous_engagements=None,
    previous_negative_scores=None
):
    """
    Complete PAWS check-in analysis.

    Combines:
    1. NLP signals
    2. Behavioural signals
    3. Self-reported well-being
    4. Emotional change
    5. Dynamic Distress Index
    6. Explainable AI

    This is a prototype screening system
    and not a clinical diagnosis.
    """

    # 1. Analyze victim's text
    nlp_result = analyze_text(text)

    # 2. Analyze behaviour/engagement
    behaviour_score = calculate_behaviour_score(
        current_engagement,
        previous_engagements
    )

    # 3. Analyze negative-emotion change
    emotional_change = calculate_emotional_change(
        nlp_result["negative_emotion_score"],
        previous_negative_scores
    )

    # 4. Calculate DDI
    ddi_result = calculate_ddi(
        fear_score=nlp_result["fear_score"],
        stress_score=nlp_result["stress_score"],
        anxiety_score=nlp_result["anxiety_score"],
        negative_emotion_score=nlp_result[
            "negative_emotion_score"
        ],
        mood_score=mood_score,
        safety_score=safety_score,
        self_report_stress=self_report_stress,
        behaviour_score=behaviour_score
    )

    # 5. Generate explanation
    explanation = generate_explanation(
        nlp_result,
        behaviour_score,
        ddi_result,
        emotional_change
    )

    return {
        "nlp": nlp_result,
        "behaviour_score": behaviour_score,
        "emotional_change": emotional_change,
        "ddi": ddi_result,
        "explanation": explanation
    }


def calculate_trend(ddi_history):
    """
    Analyze DDI values and determine overall trend.

    This is a prototype trend indicator,
    not a clinical prediction.
    """

    if not ddi_history or len(ddi_history) < 2:
        return {
            "trend": "INSUFFICIENT_DATA",
            "change": 0
        }

    # Use first and latest DDI values
    first_score = float(ddi_history[0])
    latest_score = float(ddi_history[-1])

    change = latest_score - first_score

    if change >= 10:
        trend = "WORSENING"

    elif change <= -10:
        trend = "IMPROVING"

    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "change": round(change, 2)
    }


if __name__ == "__main__":

    print("\n🐾 PAWS AI ENGINE TEST")
    print("----------------------")

    test_history = [32, 41, 56, 74]

    trend_result = calculate_trend(
        test_history
    )

    print("Trend:")
    print(trend_result)

    print("\nEmotional Change:")

    emotional_result = calculate_emotional_change(
        current_negative_score=75,
        previous_scores=[20, 30, 40]
    )

    print(emotional_result)

    print("\nComplete Check-in Analysis:")

    analysis = analyze_checkin(
        text=(
            "Mujhe bahut darr lag raha hai. "
            "Mujhe anxiety aur stress ho raha hai. "
            "Main unsafe feel kar rahi hoon."
        ),
        mood_score=2,
        safety_score=2,
        self_report_stress=9,
        current_engagement=35,
        previous_engagements=[80, 75, 70],
        previous_negative_scores=[20, 30, 40]
    )

    print(analysis)