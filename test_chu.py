# test_pictionary.py
import pygame
import sys
from hand_tracker import HandTracker
from ai_gesture_classifier import AIGestureClassifier
from minigame_pictionary import PictionaryGame

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1360, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Test Pictionary Mini Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 56)

    # Khởi tạo tracker tay
    tracker = HandTracker(width=640, height=480, alpha=0.3)
    tracker.start()

    # Khởi tạo AI nhận diện cử chỉ
    classifier = AIGestureClassifier(model_path="gesture_model.pkl", stable_frames=4)

    # Chạy mini game Pictionary
    game = PictionaryGame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier)
    result = game.run()

    print("Kết quả mini game:", "NHẬN BUFF" if result else "KHÔNG NHẬN BUFF")
    tracker.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()