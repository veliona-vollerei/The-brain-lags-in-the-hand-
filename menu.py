import pygame
import sys
import socket
from network import Network
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
PURPLE = (200, 0, 200)
ORANGE = (255, 150, 0)
BG_COLOR = (15, 15, 30)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class Button:
    def __init__(self, x, y, width, height, text, font, color=WHITE, hover_color=YELLOW, bg_color=None, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.bg_color = bg_color
        self.border_radius = border_radius
        self.is_hovered = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        text_color = self.hover_color if self.is_hovered else self.color

        if self.bg_color:
            bg = self.bg_color
            if self.is_hovered:
                bg = tuple(min(c + 30, 255) for c in bg)
            pygame.draw.rect(screen, bg, self.rect, border_radius=self.border_radius)
        else:
            pygame.draw.rect(screen, text_color, self.rect, width=2, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val, font):
        self.rect = pygame.Rect(x, y, width, 6)
        self.knob_radius = 10
        self.min = min_val
        self.max = max_val
        self.value = start_val
        self.font = font
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_knob_rect().collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            ratio = (rel_x - self.rect.left) / self.rect.width
            self.value = self.min + ratio * (self.max - self.min)

    def get_knob_rect(self):
        ratio = (self.value - self.min) / (self.max - self.min)
        knob_x = self.rect.left + int(ratio * self.rect.width)
        return pygame.Rect(knob_x - self.knob_radius, self.rect.centery - self.knob_radius,
                            self.knob_radius * 2, self.knob_radius * 2)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=3)
        active_width = int((self.value - self.min) / (self.max - self.min) * self.rect.width)
        if active_width > 0:
            pygame.draw.rect(screen, CYAN, (self.rect.left, self.rect.top, active_width, self.rect.height), border_radius=3)
        pygame.draw.circle(screen, WHITE, self.get_knob_rect().center, self.knob_radius)
        val_text = self.font.render(f"{self.value:.0f}" if isinstance(self.value, float) else str(self.value), True, WHITE)
        screen.blit(val_text, (self.rect.right + 15, self.rect.centery - 10))

class Menu:
    def __init__(self, screen, clock, font, big_font, huge_font):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.big_font = big_font
        self.huge_font = huge_font
        self.SCREEN_W, self.SCREEN_H = screen.get_size()

        self.state = "main"
        self.selected_chapter = None
        self.difficulty = 1
        self.volume = 0.7
        self.fps = 60
        self.resolution = (1360, 768)

    def draw_background(self):
        for i in range(self.SCREEN_H):
            color = (15 + i // 20, 15 + i // 30, 30 + i // 15)
            pygame.draw.line(self.screen, color, (0, i), (self.SCREEN_W, i))

    def main_menu(self):
        self.state = "main"
        title_text = self.huge_font.render("FRIDAY NIGHT FUNKIN'", True, CYAN)
        subtitle = self.font.render("Gesture Edition", True, WHITE)

        buttons = [
            Button(self.SCREEN_W//2 - 100, 300, 200, 50, "PLAY", self.big_font, GREEN, CYAN, (30, 30, 60)),
            Button(self.SCREEN_W//2 - 100, 380, 200, 50, "SETTINGS", self.big_font, WHITE, YELLOW, (30, 30, 60)),
            Button(self.SCREEN_W//2 - 100, 460, 200, 50, "EXIT", self.big_font, RED, YELLOW, (30, 30, 60)),
        ]

        running = True
        while running and self.state == "main":
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                for btn in buttons:
                    if btn.is_clicked(event):
                        if btn.text == "PLAY":
                            return "play"
                        elif btn.text == "SETTINGS":
                            return "settings"
                        elif btn.text == "EXIT":
                            pygame.quit()
                            sys.exit()

            self.draw_background()
            self.screen.blit(title_text, (self.SCREEN_W//2 - title_text.get_width()//2, 150))
            self.screen.blit(subtitle, (self.SCREEN_W//2 - subtitle.get_width()//2, 240))
            for btn in buttons:
                btn.draw(self.screen)
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()

    def play_menu(self):
        self.state = "play"
        buttons = [
            Button(self.SCREEN_W//2 - 150, 250, 300, 50, "STORY MODE", self.big_font, GREEN, CYAN, (30, 30, 60)),
            Button(self.SCREEN_W//2 - 150, 340, 300, 50, "FREE PLAY", self.big_font, ORANGE, YELLOW, (30, 30, 60)),
            Button(self.SCREEN_W//2 - 150, 430, 300, 50, "VERSUS (LAN)", self.big_font, CYAN, YELLOW, (30, 30, 60)),
            Button(self.SCREEN_W//2 - 150, 520, 300, 50, "BACK", self.big_font, RED, WHITE, (30, 30, 60)),
        ]

        running = True
        while running and self.state == "play":
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "main"

                for btn in buttons:
                    if btn.is_clicked(event):
                        if btn.text == "STORY MODE":
                            return "story"
                        elif btn.text == "FREE PLAY":
                            return "freeplay"
                        elif btn.text == "VERSUS (LAN)":
                            return "versus"
                        elif btn.text == "BACK":
                            return "main"

            self.draw_background()
            title = self.big_font.render("SELECT MODE", True, CYAN)
            self.screen.blit(title, (self.SCREEN_W//2 - title.get_width()//2, 150))
            for btn in buttons:
                btn.draw(self.screen)
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()

    def story_menu(self):
        self.state = "story"
        chapters = [
            {"name": "Chapter 1: Tutorial", "difficulty": 1, "base_speed": 2, "desc": "Huong dan co ban"},
            {"name": "Chapter 2: Bopeebo", "difficulty": 2, "base_speed": 2.5, "desc": "Do kho trung binh"},
            {"name": "Chapter 3: Fresh", "difficulty": 3, "base_speed": 3, "desc": "Do kho cao"},
        ]

        buttons = []
        y_start = 250
        for i, ch in enumerate(chapters):
            btn_text = f"{ch['name']} ({ch['difficulty']})"
            btn = Button(self.SCREEN_W//2 - 200, y_start + i * 70, 400, 50, btn_text, self.font, WHITE, YELLOW, (30, 30, 60))
            buttons.append((btn, ch))

        back_btn = Button(self.SCREEN_W//2 - 100, y_start + 3 * 70 + 20, 200, 50, "BACK", self.big_font, RED, WHITE, (30, 30, 60))

        running = True
        while running and self.state == "story":
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "play"

                for btn, ch in buttons:
                    if btn.is_clicked(event):
                        self.selected_chapter = ch
                        self.difficulty = i + 1
                        return "start_game"
                if back_btn.is_clicked(event):
                    return "play"

            self.draw_background()
            title = self.big_font.render("STORY MODE", True, GREEN)
            self.screen.blit(title, (self.SCREEN_W//2 - title.get_width()//2, 150))
            for btn, ch in buttons:
                btn.draw(self.screen)
                desc_text = self.font.render(ch["desc"], True, GRAY)
                self.screen.blit(desc_text, (btn.rect.right + 20, btn.rect.centery - 10))
            back_btn.draw(self.screen)
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()

    def freeplay_menu(self):
        self.state = "freeplay"
        chapters = [
            {"name": "Track 1: Warm-up", "difficulty": 1, "base_speed": 2.5},
            {"name": "Track 2: Getting Started", "difficulty": 2, "base_speed": 2.8},
            {"name": "Track 3: Intermediate", "difficulty": 2, "base_speed": 3.2},
            {"name": "Track 4: Advanced", "difficulty": 3, "base_speed": 3.5},
            {"name": "Track 5: Expert", "difficulty": 3, "base_speed": 4},
        ]

        buttons = []
        y_start = 220
        for i, ch in enumerate(chapters):
            btn_text = ch["name"]
            btn = Button(self.SCREEN_W//2 - 200, y_start + i * 60, 400, 45, btn_text, self.font, WHITE, YELLOW, (30, 30, 60))
            buttons.append((btn, ch))

        back_btn = Button(self.SCREEN_W//2 - 100, y_start + 5 * 60 + 20, 200, 50, "BACK", self.big_font, RED, WHITE, (30, 30, 60))

        running = True
        while running and self.state == "freeplay":
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "play"

                for btn, ch in buttons:
                    if btn.is_clicked(event):
                        self.selected_chapter = ch
                        self.difficulty = 3
                        return "start_game"
                if back_btn.is_clicked(event):
                    return "play"

            self.draw_background()
            title = self.big_font.render("FREE PLAY", True, ORANGE)
            self.screen.blit(title, (self.SCREEN_W//2 - title.get_width()//2, 150))
            for btn, ch in buttons:
                btn.draw(self.screen)
            back_btn.draw(self.screen)
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()

    def settings_menu(self):
        self.state = "settings"
        vol_slider = Slider(self.SCREEN_W//2 - 150, 300, 300, 0, 1, self.volume, self.font)

        fps_options = [30, 60]
        fps_index = fps_options.index(self.fps) if self.fps in fps_options else 0

        res_options = [(960, 540), (1360, 768), (1920, 1080)]
        res_index = res_options.index(self.resolution) if self.resolution in res_options else 1

        running = True
        while running and self.state == "settings":
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "main"

                vol_slider.handle_event(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    fps_index = (fps_index - 1) % len(fps_options)
                    self.fps = fps_options[fps_index]
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    fps_index = (fps_index + 1) % len(fps_options)
                    self.fps = fps_options[fps_index]

                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    res_index = (res_index - 1) % len(res_options)
                    self.resolution = res_options[res_index]
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    res_index = (res_index + 1) % len(res_options)
                    self.resolution = res_options[res_index]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    back_btn = Button(self.SCREEN_W//2 - 100, 550, 200, 50, "SAVE & BACK", self.big_font, GREEN, CYAN, (30, 30, 60))
                    if back_btn.is_clicked(event):
                        self.volume = vol_slider.value
                        return "main"

            self.draw_background()
            title = self.big_font.render("SETTINGS", True, CYAN)
            self.screen.blit(title, (self.SCREEN_W//2 - title.get_width()//2, 100))

            vol_text = self.font.render("Volume:", True, WHITE)
            self.screen.blit(vol_text, (self.SCREEN_W//2 - 200, 280))
            vol_slider.draw(self.screen)
            self.volume = vol_slider.value

            fps_text = self.font.render(f"FPS: {self.fps} (Left/Right to change)", True, WHITE)
            self.screen.blit(fps_text, (self.SCREEN_W//2 - 200, 380))

            res_text = self.font.render(f"Resolution: {self.resolution[0]}x{self.resolution[1]} (Up/Down to change)", True, WHITE)
            self.screen.blit(res_text, (self.SCREEN_W//2 - 200, 450))

            back_btn = Button(self.SCREEN_W//2 - 100, 550, 200, 50, "SAVE & BACK", self.big_font, GREEN, CYAN, (30, 30, 60))
            back_btn.draw(self.screen)

            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()

    # menu.py - hàm versus_menu (thay thế toàn bộ)

    def versus_menu(self):
        self.state = "versus"
        screen = self.screen
        screen_w = self.SCREEN_W
        screen_h = self.SCREEN_H

        host_btn = Button(screen_w//2 - 150, 200, 300, 50, "TẠO PHÒNG (Host)", self.big_font, GREEN, CYAN, (30,30,60))
        back_btn = Button(screen_w//2 - 150, 500, 300, 50, "BACK", self.big_font, RED, WHITE, (30,30,60))

        join_mode = False
        rooms = []
        last_scan = 0

        running = True
        while running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "play"

                if not join_mode:
                    if host_btn.is_clicked(event):
                        import random
                        room_code = str(random.randint(100, 999))
                        return ("host", room_code)
                    join_btn = Button(screen_w//2 - 150, 280, 300, 50, "THAM GIA (Client)", self.big_font, ORANGE, YELLOW, (30,30,60))
                    if join_btn.is_clicked(event):
                        join_mode = True
                    if back_btn.is_clicked(event):
                        return "play"
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        y = 280
                        for room in rooms:
                            rect = pygame.Rect(screen_w//2 - 200, y, 400, 40)
                            if rect.collidepoint(event.pos):
                                return ("join", room["ip"], room["room_code"], "Player")
                            y += 50

            self.draw_background()
            title = self.big_font.render("VERSUS - LAN", True, CYAN)
            self.screen.blit(title, (screen_w//2 - title.get_width()//2, 80))

            if not join_mode:
                host_btn.draw(screen)
                join_btn = Button(screen_w//2 - 150, 280, 300, 50, "THAM GIA (Client)", self.big_font, ORANGE, YELLOW, (30,30,60))
                join_btn.draw(screen)
                back_btn.draw(screen)
            else:
                if now - last_scan > 2000:
                    rooms = Network.scan_rooms()
                    last_scan = now
                self.screen.blit(self.font.render("Danh sách phòng:", True, WHITE), (screen_w//2 - 100, 220))
                y = 280
                for room in rooms:
                    text = f"Phòng {room['room_code']} - Host: {room['host_name']} ({room['player_count']}/2)"
                    surf = self.font.render(text, True, CYAN)
                    rect = pygame.Rect(screen_w//2 - 200, y, 400, 40)
                    pygame.draw.rect(screen, (30,30,60), rect, border_radius=8)
                    pygame.draw.rect(screen, CYAN, rect, 2, border_radius=8)
                    screen.blit(surf, (rect.x + 10, rect.y + 10))
                    y += 50
                if not rooms:
                    self.screen.blit(self.font.render("Đang tìm phòng...", True, GRAY), (screen_w//2 - 100, 280))
                back_btn2 = Button(screen_w//2 - 100, 550, 200, 50, "QUAY LẠI", self.big_font, RED, WHITE, (30,30,60))
                back_btn2.draw(screen)
                if back_btn2.is_clicked(event):
                    join_mode = False

            pygame.display.flip()