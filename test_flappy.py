import pygame
import sys
from hand_tracker import HandTracker
from ai_gesture_classifier import AIGestureClassifier
from minigame_flappy import run_flappy_minigame

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1360, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Test Flappy Bird Mini Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 56)

    # Khởi tạo tracker và classifier
    print("Đang khởi tạo webcam và AI...")
    tracker = HandTracker(width=640, height=480, alpha=0.3)
    tracker.start()
    classifier = AIGestureClassifier(stable_frames=4)

    print("\n=== TEST FLAPPY BIRD MINI GAME ===")
    print("🖐️  Xoe ban tay (RIGHT gesture) de nhay")
    print("🎯 Vượt qua 5 cột để thắng")
    print("❌ ESC để thoát")
    print("===================================\n")

    # Chạy mini game (không có background game chính)
    result = run_flappy_minigame(
        screen, clock, SCREEN_W, SCREEN_H,
        font, big_font, tracker, classifier,
        game_background=None
    )

    if result:
        print("\n✅ Kết quả: THẮNG - Nhận được buff!")
    else:
        print("\n❌ Kết quả: THUA - Không nhận được buff!")

    print("Đang thoát...")
    tracker.stop()
    tracker.join()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()