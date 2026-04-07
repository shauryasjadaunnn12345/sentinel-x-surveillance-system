import cv2
import time
import os
import random
import sys
import numpy as np
from datetime import datetime

# Import local modules
from threat_logic import calculate_threat

# CONFIGURATION
WINDOW_NAME = "SENTINEL-X :: DEFENCE SURVEILLANCE"
SAVE_FOLDER = "captures"
ALARM_COOLDOWN = 3  # Seconds between alarms to prevent spam

# Initialize Camera (0 is usually the default webcam)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Could not access webcam.")
    sys.exit()

# Create captures directory if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# --- SIMULATED AI DETECTOR (MOCKING YOLO) ---
class SimulatedYOLO:
    """
    Simulates YOLO detections for the purpose of a software-only demo.
    """
    def __init__(self):
        self.classes = ['person', 'drone', 'animal']
        self.frame_count = 0

    def detect(self, frame):
        self.frame_count += 1
        detections = []

        # Simulation Logic: Randomly spawn an object periodically
        if self.frame_count % 60 == 0 or (self.frame_count % 30 == 0 and random.random() > 0.7):
            h, w, _ = frame.shape
            
            # Pick a random class
            label = random.choice(self.classes)
            
            # Define random bounding box
            box_w = random.randint(50, 200)
            box_h = random.randint(50, 200)
            x = random.randint(0, w - box_w)
            y = random.randint(0, h - box_h)
            
            # Random confidence
            conf = round(random.uniform(0.70, 0.99), 2)
            
            detections.append({
                "box": (x, y, box_w, box_h),
                "label": label,
                "confidence": conf
            })
        
        return detections

detector = SimulatedYOLO()

def play_alarm_sound():
    """Plays a system beep sound (Cross-platform)."""
    print("🚨 ALERT 🚨")
    try:
        import winsound
        winsound.Beep(1000, 500) # Frequency 1000Hz, Duration 500ms
    except:
        print("\a") # Fallback for Mac/Linux

def draw_hud(frame, threat_data, fps):
    """
    Draws the professional Defence-style UI Overlay.
    """
    h, w, _ = frame.shape
    overlay = frame.copy()
    
    # 1. Color Coding based on Threat Level
    level = threat_data['level']
    if level == "HIGH":
        color = (0, 0, 255)      # RED
        status_color = (0, 0, 255)
    elif level == "MEDIUM":
        color = (0, 165, 255)    # ORANGE/YELLOW
        status_color = (0, 255, 255)
    else:
        color = (0, 255, 0)      # GREEN
        status_color = (0, 255, 0)

    # 2. Side Brackets (Scope look)
    cv2.line(overlay, (20, 20), (20, h-20), color, 2)
    cv2.line(overlay, (w-20, 20), (w-20, h-20), color, 2)
    cv2.line(overlay, (20, 20), (50, 20), color, 2)
    cv2.line(overlay, (20, h-20), (50, h-20), color, 2)
    cv2.line(overlay, (w-20, 20), (w-50, 20), color, 2)
    cv2.line(overlay, (w-20, h-20), (w-50, h-20), color, 2)

    # 3. Top-Left: Threat Details Panel
    panel_rect = np.zeros((160, 300, 3), dtype=np.uint8)
    panel_rect[:] = (30, 30, 30) # Dark Grey Background
    overlay[10:170, 10:310] = cv2.addWeighted(overlay[10:170, 10:310], 0.6, panel_rect, 0.4, 0)
    
    cv2.putText(overlay, "THREAT ANALYSIS", (20, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(overlay, f"TARGET: {threat_data['label']}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(overlay, f"LEVEL : {level}", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(overlay, f"SCORE : {threat_data['score']}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    cv2.putText(overlay, f"DIST  : {threat_data['distance']}m", (20, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 4. Top-Right: System Status
    cv2.putText(overlay, "SYSTEM STATUS: ACTIVE", (w - 280, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)
    cv2.putText(overlay, f"FPS: {int(fps)}", (w - 80, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Blinking REC indicator
    if (int(time.time()) * 2) % 2 == 0:
        cv2.circle(overlay, (w - 30, 30), 8, (0, 0, 255), -1)
        cv2.putText(overlay, "REC", (w - 55, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # 5. Bottom Center: Distance Ruler
    cv2.line(overlay, (w//2 - 100, h-30), (w//2 + 100, h-30), (100, 100, 100), 2)
    cv2.line(overlay, (w//2, h-40), (w//2, h-20), (100, 100, 100), 2)
    cv2.putText(overlay, "SCANNING PERIMETER...", (w//2 - 110, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    return overlay

# --- MAIN LOOP ---
prev_time = time.time() # FIX: Initialize FPS timer
last_alarm_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for uniform processing
    frame = cv2.resize(frame, (800, 600))

    # 1. Get FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    # 2. Object Detection (Simulated YOLO)
    detections = detector.detect(frame)

    # Default State
    current_threat = {
        "label": "SCANNING...",
        "level": "LOW",
        "score": 0.0,
        "distance": 0
    }
    detected_obj = None

    # Process detections (Take the highest confidence detection)
    if detections:
        best_det = max(detections, key=lambda x: x['confidence'])
        x, y, w, h = best_det['box']
        label = best_det['label']
        conf = best_det['confidence']

        # 3. Calculate Distance (FIX: Clamped formula)
        # Safe_w prevents division by zero. 
        # min/max ensures distance stays between 1m and 100m
        safe_w = max(w, 1)
        distance = int(min(100, max(1, 800 / safe_w)))

        # 4. Threat Logic Calculation
        level, score = calculate_threat(label, conf, distance)
        
        current_threat = {
            "label": label,
            "level": level,
            "score": score,
            "distance": distance
        }
        detected_obj = best_det

    # 5. Draw UI
    frame = draw_hud(frame, current_threat, fps)

    # 6. Handle Detected Object
    if detected_obj:
        x, y, w, h = detected_obj['box']
        color = (0, 0, 255) if current_threat['level'] == "HIGH" else (0, 255, 0)
        
        # Draw Bounding Box
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Draw Label Tag
        label_text = f"{detected_obj['label'].upper()} {detected_obj['confidence']}"
        cv2.rectangle(frame, (x, y-30), (x + len(label_text)*15, y), color, -1)
        cv2.putText(frame, label_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 7. HIGH THREAT ACTIONS
        if current_threat['level'] == "HIGH":
            # Flash effect (Red overlay with transparency)
            red_overlay = np.zeros_like(frame, dtype=np.uint8)
            red_overlay[:] = (0, 0, 255)
            frame = cv2.addWeighted(frame, 0.7, red_overlay, 0.3, 0)
            
            cv2.putText(frame, "!!! HIGH THREAT DETECTED !!!", (200, 300), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

            # Trigger Alarm (with cooldown)
            if curr_time - last_alarm_time > ALARM_COOLDOWN:
                play_alarm_sound()
                # Auto Screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{SAVE_FOLDER}/threat_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[ALERT] Threat Saved: {filename}")
                last_alarm_time = curr_time

    # Show Frame
    cv2.imshow(WINDOW_NAME, frame)

    # Exit on 'q' or ESC
    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

cap.release()
cv2.destroyAllWindows()
