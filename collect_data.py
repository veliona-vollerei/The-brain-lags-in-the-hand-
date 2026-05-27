# collect_data.py
import cv2
import mediapipe as mp
import csv
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def extract_features(hand_landmarks):
    lm = hand_landmarks.landmark
    base_x, base_y, base_z = lm[0].x, lm[0].y, lm[0].z
    scale = math.hypot(lm[9].x - base_x, lm[9].y - base_y)
    if scale == 0: scale = 1e-6
    
    features = []
    for i in range(21):
        features.extend([
            (lm[i].x - base_x) / scale,
            (lm[i].y - base_y) / scale,
            (lm[i].z - base_z) / scale
        ])
    return features

cap = cv2.VideoCapture(0)
DATA_FILE = "gesture_dataset.csv"
current_label = "NONE"
is_recording = False

print("Phím điều khiển:")
print("U: UP | D: DOWN | L: LEFT | R: RIGHT | N: NONE")
print("Space: Bật/Tắt thu thập dữ liệu | Q: Thoát")

with open(DATA_FILE, mode='a', newline='') as f:
    writer = csv.writer(f)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                if is_recording:
                    features = extract_features(hand_landmarks)
                    writer.writerow([current_label] + features)
                    
        cv2.putText(frame, f"Label: {current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        status = "RECORDING" if is_recording else "PAUSED"
        color = (0, 0, 255) if is_recording else (0, 255, 0)
        cv2.putText(frame, status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imshow("Collect Data", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'): break
        elif key == 32: is_recording = not is_recording # Space bar
        elif key == ord('u'): current_label = "UP"
        elif key == ord('d'): current_label = "DOWN"
        elif key == ord('l'): current_label = "LEFT"
        elif key == ord('r'): current_label = "RIGHT"
        elif key == ord('n'): current_label = "NONE"

cap.release()
cv2.destroyAllWindows()