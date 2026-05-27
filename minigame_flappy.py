# minigame_flappy.py
import pygame
import random
import sys
from utils import cv2_to_pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BG_SKY = (135, 206, 235)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.gravity = 0.1       
        self.jump_strength = -7.5  
        self.size = 20

    def jump(self):
        self.vy = self.jump_strength

    def update(self):
        self.vy += self.gravity
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x - 5), int(self.y - 5)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 5), int(self.y - 5)), 3)
        pygame.draw.polygon(screen, RED, [(self.x, self.y + 5), (self.x + 10, self.y), (self.x - 10, self.y)])

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class Pipe:
    def __init__(self, x, gap_y, gap_size=150):
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.width = 60
        self.speed = 3
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen, screen_height):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap_size // 2)
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size // 2, self.width, screen_height - (self.gap_y + self.gap_size // 2))
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, GREEN, bottom_rect)
        pygame.draw.rect(screen, (0, 150, 0), top_rect, width=3)
        pygame.draw.rect(screen, (0, 150, 0), bottom_rect, width=3)

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap_size // 2)
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size // 2, self.width, 768)
        return top_rect, bottom_rect

    def is_off_screen(self):
        return self.x + self.width < 0

# Thêm sound_manager vào hàm để nhận module âm thanh từ main
def run_flappy_minigame(screen, clock, screen_w, screen_h, font, big_font, tracker, classifier, game_background, sound_manager=None):
    """
    Mini game Flappy Bird.
    Điều khiển: xòe bàn tay (RIGHT) để chim nhảy.
    Vượt qua 5 cột để nhận buff.
    """
    bird = Bird(150, screen_h // 2)
    pipes = []
    score = 0
    target_score = 5
    game_speed = 60

    gap_y = random.randint(150, screen_h - 150)
    pipes.append(Pipe(screen_w + 100, gap_y))

    prev_gesture = "NONE"
    game_active = False       
    result = None
    result_timer = 0

    countdown = 4  
    countdown_text = "3"
    countdown_timer = 0
    COUNTDOWN_DURATION = 60  

    running = True
    while running:
        dt = clock.tick(game_speed) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        landmarks, handedness = tracker.get_landmarks()
        gesture = "NONE"
        if landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            gesture = classifier.classify(landmarks[hand_idx])

        if countdown > 0:
            countdown_timer += 1
            if countdown_timer >= COUNTDOWN_DURATION:
                countdown_timer = 0
                countdown -= 1
                if countdown == 3:
                    countdown_text = "3"
                elif countdown == 2:
                    countdown_text = "2"
                elif countdown == 1:
                    countdown_text = "1"
                elif countdown == 0:
                    countdown_text = "GO!"
                    game_active = True  
                    bird = Bird(150, screen_h // 2)
                    pipes = []
                    gap_y = random.randint(150, screen_h - 150)
                    pipes.append(Pipe(screen_w + 100, gap_y))
                    score = 0
                    result = None
                else:
                    countdown = -1  

        if game_active and result is None:
            if gesture == "RIGHT" and prev_gesture != "RIGHT":
                bird.jump()
                if sound_manager:
                    sound_manager.play_sfx("jump", volume=0.7) # Phát tiếng vỗ cánh
            prev_gesture = gesture

            bird.update()

            if bird.y < 0 or bird.y > screen_h:
                game_active = False
                result = False
                result_timer = 180
                if sound_manager: sound_manager.play_sfx("miss")

            if not pipes or pipes[-1].x < screen_w - 300:
                gap_y = random.randint(150, screen_h - 150)
                pipes.append(Pipe(screen_w + 100, gap_y))

            for pipe in pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    pipes.remove(pipe)
                    continue

                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    if score >= target_score:
                        game_active = False
                        result = True
                        result_timer = 180

                bird_rect = bird.get_rect()
                top_rect, bottom_rect = pipe.get_rects()
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    game_active = False
                    result = False
                    result_timer = 180
                    if sound_manager: sound_manager.play_sfx("miss")

        elif result is not None:
            result_timer -= 1
            if result_timer <= 0:
                running = False

        screen.fill(BG_SKY)

        for pipe in pipes:
            pipe.draw(screen, screen_h)

        if countdown > 0 or game_active or result is not None:
            bird.draw(screen)

        score_text = big_font.render(f"{score}/{target_score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        guide_text = font.render("Xoe ban tay de nhay | ESC thoat", True, WHITE)
        screen.blit(guide_text, (20, screen_h - 40))

        if countdown > 0:
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            cd_surf = big_font.render(countdown_text, True, WHITE)
            cd_rect = cd_surf.get_rect(center=(screen_w // 2, screen_h // 2))
            shadow_surf = big_font.render(countdown_text, True, (50, 50, 50))
            shadow_rect = shadow_surf.get_rect(center=(screen_w // 2 + 5, screen_h // 2 + 5))
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(cd_surf, cd_rect)

        if result is not None:
            if result:
                msg = "CHUC MUNG! BAN DA NHAN BUFF!"
                color = GREEN
            else:
                msg = "THAT BAI! KHONG NHAN DUOC BUFF!"
                color = RED
            r_surf = big_font.render(msg, True, color)
            screen.blit(r_surf, (screen_w // 2 - r_surf.get_width() // 2, screen_h // 2 - 50))

        debug_bgr = tracker.get_debug_frame()
        if debug_bgr is not None:
            cam_w, cam_h = 640, 480
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(int(cam_w * 0.2), int(cam_h * 0.2)))
            screen.blit(debug_surf, (screen_w - 160, 20))

        pygame.display.flip()

    return result == True