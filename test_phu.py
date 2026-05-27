import pygame
import sys
from hand_tracker import HandTracker
from ai_gesture_classifier import AIGestureClassifier
from minigame_millionaire import run_minigame

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1360, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Test Ai là triệu phú Mini Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 56)

    print("Đang khởi tạo webcam và AI...")
    tracker = HandTracker(width=640, height=480, alpha=0.3)
    tracker.start()
    classifier = AIGestureClassifier(stable_frames=4)

    print("\n=== TEST AI LÀ TRIỆU PHÚ ===")
    print("✊ Nắm tay di chuyển con trỏ")
    print("👍 Xác nhận đáp án")
    print("❌ ESC để thoát")
    print("===================================\n")

    result = run_minigame(
        screen, clock, SCREEN_W, SCREEN_H,
        font, big_font, tracker, classifier,
        game_background=None
    )

    if result:
        print("\n✅ Kết quả: ĐÚNG - Nhận buff!")
    else:
        print("\n❌ Kết quả: SAI hoặc thoát - Không nhận buff!")

    print("Đang thoát...")
    tracker.stop()
    tracker.join()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()