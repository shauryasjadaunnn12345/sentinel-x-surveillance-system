def calculate_threat(label, confidence, distance):
    # Base threat weights
    weights = {
        "person": 0.6,
        "drone": 0.9,
        "animal": 0.2
    }

    # Distance factor
    if distance < 50:
        dist_factor = 1.0
    elif distance < 100:
        dist_factor = 0.7
    else:
        dist_factor = 0.4

    # Get base weight
    base_weight = weights.get(label, 0.3)

    # Calculate threat score
    score = round(base_weight * confidence * dist_factor, 2)

    # Assign threat level
    if score > 0.7:
        level = "HIGH"
    elif score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, score
