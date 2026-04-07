def calculate_threat(label, confidence, distance):
    """
    Calculates the threat level and raw score based on object type and proximity.
    
    Args:
        label (str): Type of object ('person', 'drone', 'animal')
        confidence (float): AI confidence (0.0 to 1.0)
        distance (int): Distance in meters
        
    Returns:
        tuple: (level_string, score_float)
    """
    
    # 1. Define Threat Weights
    # Drones are considered highest threat (air surveillance/suicide drones)
    # Humans are medium (intrusion)
    # Animals are low (false positive prevention)
    weights = {
        "person": 0.6,
        "drone": 0.95,   # High weight for drones
        "animal": 0.15
    }
    
    # 2. Calculate Distance Factor
    # The closer the object, the higher the factor
    if distance < 10:
        dist_factor = 1.5  # Critical proximity
    elif distance < 30:
        dist_factor = 1.2  # Danger zone
    elif distance < 80:
        dist_factor = 0.8  # Caution zone
    else:
        dist_factor = 0.4  # Far away
        
    # 3. Compute Score
    # Formula: Weight * Confidence * Distance Factor
    weight = weights.get(label, 0.3)
    score = round(weight * confidence * dist_factor, 3)
    
    # 4. Determine Classification Level
    if score >= 0.8:
        level = "HIGH"
    elif score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return level, score
