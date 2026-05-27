# minigame_king_vietnamese.py
import pygame
import sys
import unicodedata
from utils import cv2_to_pygame
from king_vietnamese_questions import get_random_question
from minigame_pictionary import VirtualKeyboard, AnswerGrid, get_vietnamese_font

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
BG_COLOR = (20, 20, 40)
CLUE_BG = (40, 40, 70)

def normalize_text(text):
    """Chuẩn hóa Unicode để tránh lỗi font"""
    return unicodedata.normalize('NFC', text)

class KingVietnameseGame:
    def __init__(self, screen, clock, screen_w, screen_h, font, big_font, tracker, classifier):
        self.screen = screen
        self.clock = clock
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font = font
        self.big_font = big_font
        self.tracker = tracker
        self.classifier = classifier

        # Font tiếng Việt
        self.vn_font = get_vietnamese_font(32)
        self.vn_big_font = get_vietnamese_font(56)

        # Lấy câu hỏi ngẫu nhiên
        self.question = get_random_question()

        # Tạo lưới ô nhập chữ
        self.grid = AnswerGrid(
            self.question["answer_nodiacritic"],
            self.question["answer_diacritic"],
            screen_w, screen_h, font, big_font
        )

        # Bàn phím ảo
        self.keyboard = VirtualKeyboard(screen_w, screen_h, font)

        # Con trỏ
        self.cursor_x = screen_w // 2
        self.cursor_y = screen_h // 2
        self.prev_wrist = None

        # Trạng thái
        self.result = None
        self.result_timer = 0
        self.show_result = False

        # Cooldown 1 giây
        self.cooldown = 0
        self.COOLDOWN_MAX = 60

    def update_cursor(self):
        landmarks, handedness = self.tracker.get_landmarks()
        current_wrist = None
        if landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            lm = landmarks[hand_idx].landmark
            current_wrist = (lm[0].x, lm[0].y)

        if self.prev_wrist and current_wrist:
            dx = (current_wrist[0] - self.prev_wrist[0]) * 1200
            dy = (current_wrist[1] - self.prev_wrist[1]) * 1200
                # Làm mượt (smoothing)
            if not hasattr(self, 'smooth_dx'):
                self.smooth_dx = 0
                self.smooth_dy = 0
            smooth_factor = 0.6  # Giá trị từ 0.5 đến 0.8
            self.smooth_dx = smooth_factor * dx + (1 - smooth_factor) * self.smooth_dx
            self.smooth_dy = smooth_factor * dy + (1 - smooth_factor) * self.smooth_dy

            self.cursor_x += self.smooth_dx
            self.cursor_y += self.smooth_dy
        self.prev_wrist = current_wrist

        self.cursor_x = max(0, min(self.screen_w, self.cursor_x))
        self.cursor_y = max(0, min(self.screen_h, self.cursor_y))

    def handle_gesture(self, gesture):
        if self.result is not None:
            return
        if self.cooldown > 0:
            return

        if gesture == "UP":
            key = self.keyboard.get_key_at_pos(self.cursor_x, self.cursor_y)
            if key is None:
                return
            if key == "XÓA":
                self.grid.update_input("XÓA")
                self.cooldown = self.COOLDOWN_MAX
            elif key == "OK":
                self.check_answer()
                self.cooldown = self.COOLDOWN_MAX
            elif key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                self.grid.update_input(key)
                self.cooldown = self.COOLDOWN_MAX

    def check_answer(self):
        player_input = self.grid.get_current_answer()
        correct_nodiacritic = self.question["answer_nodiacritic"].replace(" ", "")
        if player_input == correct_nodiacritic:
            self.result = True
        else:
            self.result = False
        self.result_timer = 180
        self.show_result = True

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Vẽ khung gợi ý
        clue_box = pygame.Rect(self.screen_w//2 - 300, 80, 600, 60)
        pygame.draw.rect(self.screen, CLUE_BG, clue_box, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, clue_box, 2, border_radius=12)

        # Gợi ý loại từ
        hint_text = normalize_text(f"Gợi ý: {self.question['hint']}")
        hint_surf = self.vn_font.render(hint_text, True, YELLOW)
        self.screen.blit(hint_surf, (clue_box.x + 20, clue_box.y + 15))

        # Hiển thị các chữ cái rời rạc với dấu '/' giữa các chữ
        clues_raw = self.question["clues"]
        clue_parts = clues_raw.split('/')
        clue_str = " / ".join(clue_parts)  # Thêm dấu / và khoảng trắng
        clue_surf = self.vn_big_font.render(normalize_text(clue_str), True, WHITE)
        clue_rect = clue_surf.get_rect(center=(self.screen_w//2, 170))
        self.screen.blit(clue_surf, clue_rect)

        # Lưới ô nhập chữ
        self.grid.draw(self.screen)

        # Bàn phím ảo
        self.keyboard.draw(self.screen)

        # Con trỏ
        pygame.draw.circle(self.screen, (255, 215, 0), (int(self.cursor_x), int(self.cursor_y)), 15)
        pygame.draw.circle(self.screen, WHITE, (int(self.cursor_x), int(self.cursor_y)), 8)

        # Hướng dẫn
        guide_text = normalize_text("Nắm tay di chuyển | 👍 (UP) chọn | XÓA xóa | OK xác nhận | ESC thoát")
        guide = self.vn_font.render(guide_text, True, GRAY)
        self.screen.blit(guide, (self.screen_w//2 - guide.get_width()//2, self.screen_h - 40))

        # Webcam nhỏ
        debug_bgr = self.tracker.get_debug_frame()
        if debug_bgr is not None:
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(128, 96))
            self.screen.blit(debug_surf, (self.screen_w - 140, 20))

        # Kết quả
        if self.show_result:
            if self.result:
                msg = normalize_text(f"CHÍNH XÁC! Đáp án: {self.question['answer_diacritic']}")
                color = GREEN
            else:
                msg = normalize_text(f"SAI! Đáp án đúng: {self.question['answer_diacritic']}")
                color = RED
            result_surf = self.vn_big_font.render(msg, True, color)
            self.screen.blit(result_surf, (self.screen_w//2 - result_surf.get_width()//2, self.screen_h - 150))

    def update(self, dt):
        self.update_cursor()
        self.keyboard.update_hover((self.cursor_x, self.cursor_y))

        if self.cooldown > 0:
            self.cooldown -= 1

        landmarks, handedness = self.tracker.get_landmarks()
        gesture = "NONE"
        if landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            gesture = self.classifier.classify(landmarks[hand_idx])
        self.handle_gesture(gesture)

        if self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer <= 0:
                return False
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            running = self.update(dt)
            self.draw()
            pygame.display.flip()
        return self.result if self.result is not None else False