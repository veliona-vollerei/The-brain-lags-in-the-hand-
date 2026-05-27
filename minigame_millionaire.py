# minigame_millionaire.py
import pygame
import random
import sys
import math
import os
from utils import cv2_to_pygame

# Màu sắc
DEEP_BLUE = (10, 15, 60)
GOLD = (255, 215, 0)
LIGHT_GOLD = (255, 240, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 50, 50)
GREEN = (0, 255, 0)

# Cập nhật câu hỏi theo yêu cầu
QUESTIONS = [
    {
        "question": "Chọn từ có cách viết đúng:",
        "answers": ["trậm trễ", "chậm chễ", "chậm trễ", "trậm chễ"],
        "correct": 2  # chậm trễ
    },
    {
        "question": "Từ nào còn thiếu trong câu tục ngữ: 'Trẻ trồng đa, già trồng ....' ?",
        "answers": ["thông", "mít", "khế", "dừa"],
        "correct": 0  # thông
    },
    {
        "question": "Đâu là loại cháo khác với các món còn lại?",
        "answers": ["cháo gà", "cháo bò", "cháo heo", "cháo vịt"],
        "correct": 2  # cháo heo (thịt heo, còn lại là gia cầm/gia súc khác)
    },
    {
        "question": "Người ta thường nấu canh cua với thứ gì?",
        "answers": ["củ cải", "mộc nhĩ", "rau đay", "xúp lơ xanh"],
        "correct": 2  # rau đay
    },
    {
        "question": "Từ nào sau đây viết đúng chính tả tiếng Việt?",
        "answers": ["chằn chọc", "chằn trọc", "trằn chọc", "trằn trọc"],
        "correct": 3  # trằn trọc
    },
    {
        "question": "Cấu trúc so sánh hơn với tính từ/trạng từ ngắn trong tiếng Anh là?",
        "answers": [
            "S + V + adj/adv-er + than + O",
            "S + V + more + adj/adv + than + O",
            "S + V + the + adj/adv-est + (Noun)",
            "S + V + the most + adj/adv + (Noun)"
        ],
        "correct": 0  # cấu trúc ngắn: adj/adv-er
    },
]

class Cursor:
    def __init__(self, screen_w, screen_h):
        self.x = screen_w // 2
        self.y = screen_h // 2
        self.size = 12
        self.sensitivity = 6      # tăng từ 4 lên 6 (nhạy hơn)
        self.smoothing = 0.5 
        self.deadzone = 0.01
        self.prev_dx = 0
        self.prev_dy = 0
        self.glow_timer = 0

    def move(self, raw_dx, raw_dy):
        if abs(raw_dx) < self.deadzone:
            raw_dx = 0
        if abs(raw_dy) < self.deadzone:
            raw_dy = 0

        smooth_dx = self.smoothing * raw_dx + (1 - self.smoothing) * self.prev_dx
        smooth_dy = self.smoothing * raw_dy + (1 - self.smoothing) * self.prev_dy
        self.prev_dx = smooth_dx
        self.prev_dy = smooth_dy

        self.x += smooth_dx * self.sensitivity * 1000
        self.y += smooth_dy * self.sensitivity * 1000

    def get_pos(self):
        return (self.x, self.y)

    def draw(self, screen):
        self.glow_timer += 1
        glow_alpha = int(100 + 80 * math.sin(self.glow_timer * 0.1))
        for r in range(20, 5, -5):
            alpha = max(0, glow_alpha - r * 2)
            pygame.draw.circle(screen, (*GOLD, alpha), (int(self.x), int(self.y)), self.size + r)
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, LIGHT_GOLD, (int(self.x), int(self.y)), self.size - 3, 2)


class AnswerButton:
    def __init__(self, x, y, width, height, text, index, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.index = index
        self.base_color = color
        self.hovered = False
        self.glow_alpha = 0

    def update(self, cursor_pos):
        self.hovered = self.rect.collidepoint(cursor_pos)
        if self.hovered:
            self.glow_alpha = min(255, self.glow_alpha + 10)
        else:
            self.glow_alpha = max(0, self.glow_alpha - 5)

    def draw(self, screen, font):
        bg_color = tuple(min(c + 80, 255) for c in self.base_color) if self.hovered else self.base_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=12)
        border_color = LIGHT_GOLD if self.hovered else GOLD
        pygame.draw.rect(screen, border_color, self.rect, width=3, border_radius=12)

        labels = ["A", "B", "C", "D"]
        label_surf = font.render(f"{labels[self.index]}.", True, LIGHT_GOLD)
        label_rect = label_surf.get_rect(midleft=(self.rect.left + 20, self.rect.centery))
        screen.blit(label_surf, label_rect)

        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 70, self.rect.centery))
        screen.blit(text_surf, text_rect)

        if self.hovered:
            glow_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            for i in range(3):
                alpha = 50 - i * 15
                pygame.draw.rect(glow_surf, (*GOLD, alpha),
                                 (5 - i, 5 - i, self.rect.width + 10 + i * 2, self.rect.height + 10 + i * 2),
                                 border_radius=12)
            screen.blit(glow_surf, (self.rect.x - 10, self.rect.y - 10))


def get_vietnamese_font(size):
    """Trả về font hỗ trợ tiếng Việt."""
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
                font = pygame.font.Font(path, size)
                print(f"✅ Sử dụng font: {path}")
                return font
            except:
                continue
    print("⚠️ Không tìm thấy font Unicode, dùng font mặc định (có thể thiếu dấu)")
    return pygame.font.Font(None, size)


def run_minigame(screen, clock, screen_w, screen_h, font, big_font, tracker, classifier, game_background):
    font_vi = get_vietnamese_font(30)
    big_font_vi = get_vietnamese_font(55)

    # Ảnh nền (giữ nguyên)
    bg_image = None
    bg_path = os.path.join("backgrounds", "H3Fu_Ai_l3Fu_ph28Kh29.jpg")
    if os.path.exists(bg_path):
        try:
            bg_image = pygame.image.load(bg_path).convert()
            bg_image = pygame.transform.scale(bg_image, (screen_w, screen_h))
        except:
            pass

    question_data = random.choice(QUESTIONS)
    question = question_data["question"]
    answers = question_data["answers"]
    correct = question_data["correct"]

    cursor = Cursor(screen_w, screen_h)

    button_colors = [
        (20, 60, 180),
        (180, 20, 20),
        (180, 150, 0),
        (20, 150, 20),
    ]

    btn_width = 400
    btn_height = 65
    h_gap = 40
    v_gap = 30
    total_width = btn_width * 2 + h_gap
    total_height = btn_height * 2 + v_gap
    start_x = screen_w // 2 - total_width // 2
    start_y = screen_h // 2 - total_height // 2 + 20

    buttons = []
    for i, ans in enumerate(answers):
        row = i // 2
        col = i % 2
        bx = start_x + col * (btn_width + h_gap)
        by = start_y + row * (btn_height + v_gap)
        buttons.append(AnswerButton(bx, by, btn_width, btn_height, ans, i, button_colors[i]))

    selected_index = -1
    confirmed = False
    result = None
    result_timer = 0

    prev_wrist = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        landmarks, handedness = tracker.get_landmarks()
        gesture = "NONE"
        current_wrist = None
        if landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            gesture = classifier.classify(landmarks[hand_idx])
            lm = landmarks[hand_idx].landmark
            current_wrist = (lm[0].x, lm[0].y)

        if prev_wrist and current_wrist:
            raw_dx = current_wrist[0] - prev_wrist[0]
            raw_dy = current_wrist[1] - prev_wrist[1]
            cursor.move(raw_dx, raw_dy)
        prev_wrist = current_wrist

        cursor.x = max(0, min(screen_w, cursor.x))
        cursor.y = max(0, min(screen_h, cursor.y))

        for btn in buttons:
            btn.update(cursor.get_pos())

        if gesture == "UP" and not confirmed and result is None:
            for btn in buttons:
                if btn.hovered:
                    selected_index = btn.index
                    confirmed = True
                    result = (selected_index == correct)
                    result_timer = 180
                    break

        # Vẽ
        if bg_image:
            screen.blit(bg_image, (0, 0))
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(DEEP_BLUE)

        logo_text = big_font_vi.render("AI LÀ TRIỆU PHÚ", True, GOLD)
        logo_rect = logo_text.get_rect(center=(screen_w // 2, 70))
        shadow_text = big_font_vi.render("AI LÀ TRIỆU PHÚ", True, (100, 80, 0))
        screen.blit(shadow_text, (logo_rect.x + 3, logo_rect.y + 3))
        screen.blit(logo_text, logo_rect)

        pygame.draw.line(screen, GOLD, (screen_w // 2 - 200, 105), (screen_w // 2 + 200, 105), 2)

        q_box = pygame.Rect(screen_w // 2 - 450, 130, 900, 70)
        pygame.draw.rect(screen, BLACK, q_box, border_radius=15)
        pygame.draw.rect(screen, GOLD, q_box, width=2, border_radius=15)
        q_surf = font_vi.render(question, True, WHITE)
        q_rect = q_surf.get_rect(center=q_box.center)
        screen.blit(q_surf, q_rect)

        for btn in buttons:
            btn.draw(screen, font_vi)

        cursor.draw(screen)

        guide = font_vi.render("Nắm tay di chuyển | 👍 xác nhận | ESC thoát", True, GRAY)
        screen.blit(guide, (screen_w // 2 - guide.get_width() // 2, screen_h - 40))

        if result is not None:
            result_timer -= 1
            if result:
                msg = "CHÚC MỪNG! BẠN ĐÃ NHẬN BUFF!"
                color = GREEN
            else:
                msg = f"SAI RỒI! Đáp án đúng là: {answers[correct]}"
                color = RED
            r_surf = big_font_vi.render(msg, True, color)
            r_rect = r_surf.get_rect(center=(screen_w // 2, screen_h // 2 + 180))
            screen.blit(r_surf, r_rect)

            if result_timer <= 0:
                running = False

        debug_bgr = tracker.get_debug_frame()
        if debug_bgr is not None:
            cam_w, cam_h = 640, 480
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(int(cam_w * 0.2), int(cam_h * 0.2)))
            screen.blit(debug_surf, (screen_w - 160, 20))

        pygame.display.flip()

    return result == True