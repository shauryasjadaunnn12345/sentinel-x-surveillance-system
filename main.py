import cv2
import random
import time
import os
from datetime import datetime
from threat_logic import calculate_threat

# Create captures folder
if not os.path.exists("captures"):
    os.makedirs("captures")

# Camera
cap = cv2.VideoCapture(0)

# Human detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# FPS calculation
prev_time = 0

def play_alarm():
    print("🚨 ALARM TRIGGERED")  # simple demo (no sound dependency)

def save_capture(frame):
    filename = datetime.now().strftime("captures/intruder_%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(filename, frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # FPS
    curr_time = time.time()
    fps = int(1 / (curr_time - prev_time)) if prev_time != 0 else 0
    prev_time = curr_time

    # Detection
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))

    threat_label = "NONE"
    threat_level = "LOW"
    threat_score = 0.0
    confidence = 0.0

    distance = random.randint(20, 150)

    for i, (x, y, w, h) in enumerate(boxes):
        confidence = round(float(weights[i]), 2)
        threat_label = "person"

        # Draw box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Threat calculation
        threat_level, threat_score = calculate_threat(
            threat_label, confidence, distance
        )

        cv2.putText(frame, f"{threat_label.upper()} ({confidence})",
                    (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # UI PANEL
    # Background box
    cv2.rectangle(frame, (0, 0), (250, 150), (0, 0, 0), -1)

    # Text UI
    cv2.putText(frame, f"Threat: {threat_label.upper()}",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, f"Level: {threat_level}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    cv2.putText(frame, f"Score: {threat_score}",
                (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    cv2.putText(frame, f"Distance: {distance} cm",
                (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)

    cv2.putText(frame, f"FPS: {fps}",
                (10, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    # System status
    cv2.putText(frame, "SYSTEM ACTIVE",
                (400, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Alert
    if threat_level == "HIGH":
        play_alarm()
        save_capture(frame)
        cv2.putText(frame, "🚨 HIGH ALERT 🚨",
                    (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    cv2.imshow("SENTINEL-X Surveillance", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
