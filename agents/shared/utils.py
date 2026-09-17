def get_risk_level(score):
    if score >= 70:
        return "LOW"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "HIGH"