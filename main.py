import cv2
import random
from threat_logic import calculate_threat

# Initialize camera
cap = cv2.VideoCapture(0)

# Load human detector (HOG + SVM)
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for faster processing
    frame = cv2.resize(frame, (640, 480))

    # Detect humans
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))

    threat_label = "NONE"
    threat_level = "LOW"
    threat_score = 0.0
    confidence = 0.0

    # Simulated sensor distance
    distance = random.randint(20, 150)

    for i, (x, y, w, h) in enumerate(boxes):
        confidence = round(float(weights[i]), 2)

        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        threat_label = "person"

        # Calculate threat
        threat_level, threat_score = calculate_threat(
            threat_label, confidence, distance
        )

        # Label near box
        cv2.putText(frame, f"{threat_label.upper()} ({confidence})",
                    (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # UI display
    cv2.putText(frame, f"Threat: {threat_label.upper()}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(frame, f"Level: {threat_level}",
                (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.putText(frame, f"Score: {threat_score}",
                (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    cv2.putText(frame, f"Distance: {distance} cm",
                (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

    # Alert
    if threat_level == "HIGH":
        cv2.putText(frame, "🚨 HIGH ALERT 🚨",
                    (180, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    # Show window
    cv2.imshow("SENTINEL-X Surveillance", frame)

    # Exit on ESC
    if cv2.waitKey(1) == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
