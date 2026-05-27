# hand_tracker.py
import cv2
import mediapipe as mp
import threading
import time

class HandTracker:
    def __init__(self, width=640, height=480, alpha=0.3):
        self.width = width
        self.height = height
        self.alpha = alpha
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        self.mp_hands = mp.solutions.hands
        # Tăng min_detection để giảm lag khi không thấy tay
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.frame = None
        self.results = None
        self.debug_frame = None
        self.smoothed_results = None
        
        self.running = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._update, daemon=True)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret: continue
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            with self.lock:
                self.frame = frame
                self.results = results
                self.debug_frame = frame.copy()
            # Tăng tần suất đọc camera một chút
            time.sleep(0.01)

    def get_landmarks(self):
        with self.lock:
            if self.results and self.results.multi_hand_landmarks:
                return self.results.multi_hand_landmarks, self.results.multi_handedness
        return None, None

    def get_debug_frame(self):
        with self.lock:
            return self.debug_frame