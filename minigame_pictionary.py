# minigame_pictionary.py
import pygame
import sys
import os
import unicodedata
from utils import cv2_to_pygame
from pictionary_questions import get_random_question

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 30, 80)
BG_COLOR = (20, 20, 40)
KEY_COLOR = (60, 60, 90)
KEY_HOVER = (100, 100, 140)
BOX_COLOR = (40, 40, 70)
BOX_BORDER = (200, 200, 200)
BOX_HIGHLIGHT = (255, 215, 0)

# Bảng chữ cái (viết hoa, không dấu)
ALPHABET = [chr(i) for i in range(ord('A'), ord('Z')+1)]
# Thay ký tự đặc biệt bằng text thuần
CONTROL_KEYS = ["XÓA", "OK"]


def get_vietnamese_font(size):
    """Trả về font hỗ trợ tiếng Việt (giống minigame_millionaire)"""
    import os
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "assets/NotoSans-Vietnamese.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.Font(None, size)


class VirtualKeyboard:
    """Bàn phím ảo (chữ cái + XÓA + OK)"""
    def __init__(self, screen_w, screen_h, font):
        self.font = font
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.key_width = 70
        self.key_height = 70
        self.gap = 10
        self.buttons = []
        self.create_layout()

    def create_layout(self):
        keys = ALPHABET[:10] + [" "] + ALPHABET[10:19] + [" "] + ALPHABET[19:] + CONTROL_KEYS
        keys = [k for k in keys if k != " "]

        x_start = (self.screen_w - (self.key_width * 10 + self.gap * 9)) // 2
        y_start = self.screen_h - 280

        for i, key in enumerate(keys):
            row = i // 10
            col = i % 10
            x = x_start + col * (self.key_width + self.gap)
            y = y_start + row * (self.key_height + self.gap)
            rect = pygame.Rect(x, y, self.key_width, self.key_height)
            self.buttons.append({
                "rect": rect,
                "key": key,
                "hover": False
            })

    def draw(self, screen):
        for btn in self.buttons:
            color = KEY_HOVER if btn["hover"] else KEY_COLOR
            pygame.draw.rect(screen, color, btn["rect"], border_radius=10)
            pygame.draw.rect(screen, WHITE, btn["rect"], 2, border_radius=10)
            text = self.font.render(btn["key"], True, WHITE)
            text_rect = text.get_rect(center=btn["rect"].center)
            screen.blit(text, text_rect)

    def get_key_at_pos(self, x, y):
        for btn in self.buttons:
            if btn["rect"].collidepoint(x, y):
                return btn["key"]
        return None

    def update_hover(self, cursor_pos):
        for btn in self.buttons:
            btn["hover"] = btn["rect"].collidepoint(cursor_pos)


class AnswerGrid:
    """Lưới ô vuông nhập chữ"""
    def __init__(self, answer_nodiacritic, answer_diacritic, screen_w, screen_h, font, big_font):
        self.answer_nodiacritic = answer_nodiacritic
        self.answer_diacritic = answer_diacritic
        self.font = font
        self.big_font = big_font
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.words = self.answer_nodiacritic.split()
        self.total_chars = sum(len(w) for w in self.words)
        self.input_chars = [''] * self.total_chars

        self.cell_size = 70
        self.cell_gap = 12
        self.word_gap = 40
        self.cells = []
        self.build_layout()

    def build_layout(self):
        total_width = 0
        for idx, word in enumerate(self.words):
            word_width = len(word) * (self.cell_size + self.cell_gap) - self.cell_gap
            total_width += word_width
            if idx < len(self.words) - 1:
                total_width += self.word_gap
        start_x = (self.screen_w - total_width) // 2
        y = 330

        current_x = start_x
        for w_idx, word in enumerate(self.words):
            for c_idx, ch in enumerate(word):
                rect = pygame.Rect(current_x, y, self.cell_size, self.cell_size)
                self.cells.append({
                    "rect": rect,
                    "word_idx": w_idx,
                    "char_idx": c_idx,
                    "expected_char": ch
                })
                current_x += self.cell_size + self.cell_gap
            if w_idx < len(self.words) - 1:
                current_x += self.word_gap

    def update_input(self, key):
        if key == "XÓA":
            for i in range(len(self.input_chars) - 1, -1, -1):
                if self.input_chars[i] != '':
                    self.input_chars[i] = ''
                    break
        elif key in ALPHABET:
            for i in range(len(self.input_chars)):
                if self.input_chars[i] == '':
                    self.input_chars[i] = key
                    break

    def get_current_answer(self):
        return ''.join(self.input_chars)

    def is_complete(self):
        return all(c != '' for c in self.input_chars)

    def draw(self, screen):
        for cell in self.cells:
            rect = cell["rect"]
            pygame.draw.rect(screen, BOX_COLOR, rect, border_radius=8)
            pygame.draw.rect(screen, BOX_BORDER, rect, 2, border_radius=8)

            idx = self.cells.index(cell)
            char = self.input_chars[idx]
            if char:
                text = self.big_font.render(char, True, YELLOW)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            else:
                line_y = rect.bottom - 10
                pygame.draw.line(screen, BOX_BORDER,
                                 (rect.left + 10, line_y),
                                 (rect.right - 10, line_y), 3)


class PictionaryGame:
    def __init__(self, screen, clock, screen_w, screen_h, font, big_font, tracker, classifier):
        self.screen = screen
        self.clock = clock
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font = font
        self.big_font = big_font
        self.tracker = tracker
        self.classifier = classifier

        # Font tiếng Việt cho thông báo
        self.vn_font = get_vietnamese_font(32)
        self.vn_big_font = get_vietnamese_font(56)

        self.question = get_random_question()
        self.image = self.load_image()

        self.grid = AnswerGrid(
            self.question["answer_nodiacritic"],
            self.question["answer_diacritic"],
            screen_w, screen_h, font, big_font
        )

        self.keyboard = VirtualKeyboard(screen_w, screen_h, font)

        self.cursor_x = screen_w // 2
        self.cursor_y = screen_h // 2
        self.prev_wrist = None

        self.result = None
        self.result_timer = 0
        self.show_result = False

        # Cooldown để tránh bấm liên tục (1 giây = 60 frame)
        self.cooldown = 0
        self.COOLDOWN_MAX = 60  # 1 giây ở 60fps

    def load_image(self):
        path = self.question["image_path"]
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                max_w = self.screen_w - 200
                max_h = 350
                w, h = img.get_size()
                scale = min(max_w / w, max_h / h)
                new_size = (int(w * scale), int(h * scale))
                img = pygame.transform.scale(img, new_size)
                return img
            except:
                pass
        surf = pygame.Surface((400, 300))
        surf.fill((80, 80, 80))
        text = self.font.render("? HÌNH ẢNH ?", True, WHITE)
        surf.blit(text, (200 - text.get_width()//2, 150 - text.get_height()//2))
        return surf

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
            return  # Đang trong thời gian chờ, không nhận lệnh mới

        if gesture == "UP":
            key = self.keyboard.get_key_at_pos(self.cursor_x, self.cursor_y)
            if key == "XÓA":
                self.grid.update_input("XÓA")
                self.cooldown = self.COOLDOWN_MAX
            elif key == "OK":
                self.check_answer()
                self.cooldown = self.COOLDOWN_MAX
            elif key in ALPHABET:
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

        # Khung hình ảnh
        img_rect = self.image.get_rect(center=(self.screen_w//2, 180))
        pygame.draw.rect(self.screen, WHITE, img_rect.inflate(10, 10), 3, border_radius=10)
        self.screen.blit(self.image, img_rect)

        # Lưới ô chữ
        self.grid.draw(self.screen)

        # Bàn phím ảo
        self.keyboard.draw(self.screen)

        # Con trỏ
        pygame.draw.circle(self.screen, (255, 215, 0), (int(self.cursor_x), int(self.cursor_y)), 15)
        pygame.draw.circle(self.screen, WHITE, (int(self.cursor_x), int(self.cursor_y)), 8)

        # Hướng dẫn (dùng font có dấu)
        guide = self.vn_font.render("Nắm tay di chuyển | 👍 (UP) chọn | XÓA xóa | OK xác nhận | ESC thoát", True, GRAY)
        self.screen.blit(guide, (self.screen_w//2 - guide.get_width()//2, self.screen_h - 40))

        # Webcam nhỏ
        debug_bgr = self.tracker.get_debug_frame()
        if debug_bgr is not None:
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(128, 96))
            self.screen.blit(debug_surf, (self.screen_w - 140, 20))

        # Hiển thị kết quả (có dấu)
        if self.show_result:
            if self.result:
                msg = f"CHÍNH XÁC! Đáp án: {self.question['answer_diacritic']}"
                color = GREEN
            else:
                msg = f"SAI! Đáp án đúng: {self.question['answer_diacritic']}"
                color = RED
            result_surf = self.vn_big_font.render(msg, True, color)
            self.screen.blit(result_surf, (self.screen_w//2 - result_surf.get_width()//2, self.screen_h - 150))

    def update(self, dt):
        self.update_cursor()
        self.keyboard.update_hover((self.cursor_x, self.cursor_y))

        # Giảm cooldown
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