def calculate_behaviour_score(current_engagement, previous_engagements=None):
    """
    Calculates a simple behavioural concern score.

    Higher score = greater behavioural concern.
    This is a prototype indicator, not a clinical assessment.
    """

    if current_engagement is None:
        current_engagement = 0

    # Keep engagement between 0 and 100
    current_engagement = max(0, min(100, float(current_engagement)))

    # Low engagement means higher concern
    concern_score = 100 - current_engagement

    # Compare with previous engagement if available
    if previous_engagements:
        previous_average = sum(previous_engagements) / len(previous_engagements)

        drop = previous_average - current_engagement

        # Add extra concern when engagement has dropped
        if drop > 0:
            concern_score += drop * 0.5

    # Keep final score between 0 and 100
    concern_score = max(0, min(100, concern_score))

    return round(concern_score, 2)
if __name__ == "__main__":
    previous = [80, 75, 70]

    score = calculate_behaviour_score(
        current_engagement=45,
        previous_engagements=previous
    )

    print("Behaviour concern score:", score)