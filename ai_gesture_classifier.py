# ai_gesture_classifier.py
import joblib
import numpy as np
import math

class AIGestureClassifier:
    def __init__(self, model_path="gesture_model.pkl", stable_frames=5):
        self.model = joblib.load(model_path)
        self.stable_frames = stable_frames
        self.current_gesture = "NONE"
        self.candidate_gesture = "NONE"
        self.candidate_count = 0

    def extract_features(self, hand_landmarks):
        lm = hand_landmarks.landmark
        base_x = lm[0].x
        base_y = lm[0].y
        base_z = lm[0].z

        lm9_x = lm[9].x
        lm9_y = lm[9].y
        scale = math.hypot(lm9_x - base_x, lm9_y - base_y)
        if scale == 0:
            scale = 1e-6

        features = []
        for i in range(21):
            rel_x = (lm[i].x - base_x) / scale
            rel_y = (lm[i].y - base_y) / scale
            rel_z = (lm[i].z - base_z) / scale
            features.extend([rel_x, rel_y, rel_z])
        return np.array(features).reshape(1, -1)

    def classify(self, hand_landmarks):
        features = self.extract_features(hand_landmarks)
        raw = self.model.predict(features)[0]

        if raw == self.candidate_gesture:
            self.candidate_count += 1
        else:
            self.candidate_gesture = raw
            self.candidate_count = 1

        if self.candidate_count >= self.stable_frames:
            self.current_gesture = self.candidate_gesture
            
        return self.current_gesture