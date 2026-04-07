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

    score = weights.get(label, 0.3) * confidence * dist_factor

    if score > 0.7:
        return "HIGH"
    elif score > 0.4:
        return "MEDIUM"
    else:
        return "LOW"
