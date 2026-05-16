def classify_fatigue(score: float) -> str:
    if score <= 40:
        return "low"
    elif score <= 69:
        return "medium"
    else:
        return "high"