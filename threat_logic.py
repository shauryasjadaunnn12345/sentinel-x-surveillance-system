def calculate_threat(label, confidence, distance):
    weights = {
        "person": 0.6,
        "drone": 0.9,
        "animal": 0.2
    }

    if distance < 50:
        dist_factor = 1.0
    elif distance < 100:
        dist_factor = 0.7
    else:
        dist_factor = 0.4

    base_weight = weights.get(label, 0.3)

    score = round(base_weight * confidence * dist_factor, 2)

    if score > 0.7:
        level = "HIGH"
    elif score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, score
