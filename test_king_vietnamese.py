# test_king_vietnamese.py
import pygame
import sys
from hand_tracker import HandTracker
from ai_gesture_classifier import AIGestureClassifier
from minigame_king_vietnamese import KingVietnameseGame

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1360, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Test Vua Tiếng Việt Mini Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 56)

    tracker = HandTracker(width=640, height=480, alpha=0.3)
    tracker.start()

    classifier = AIGestureClassifier(model_path="gesture_model.pkl", stable_frames=4)

    game = KingVietnameseGame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier)
    result = game.run()

    print("Kết quả mini game:", "NHẬN BUFF" if result else "KHÔNG NHẬN BUFF")
    tracker.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()