import pygame
import os
import math

ARROW_COLORS = {
    "UP":    (0, 255, 0),
    "DOWN":  (255, 0, 0),
    "LEFT":  (255, 255, 0),
    "RIGHT": (0, 0, 255)
}

def draw_arrow(screen, cx, cy, direction, size=50, color=None, alpha=255):
    if color is None:
        color = ARROW_COLORS[direction]
    pts = []
    if direction == "LEFT":
        pts = [(cx - size//3, cy), (cx + size//6, cy - size//4), (cx + size//6, cy + size//4)]
    elif direction == "DOWN":
        pts = [(cx, cy + size//3), (cx - size//4, cy - size//6), (cx + size//4, cy - size//6)]
    elif direction == "UP":
        pts = [(cx, cy - size//3), (cx - size//4, cy + size//6), (cx + size//4, cy + size//6)]
    elif direction == "RIGHT":
        pts = [(cx + size//3, cy), (cx - size//6, cy - size//4), (cx - size//6, cy + size//4)]
    pygame.draw.polygon(screen, color, pts)

class Receptor:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = ARROW_COLORS[direction]
        self.size = 60

    def draw(self, screen):
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=10)
        pygame.draw.rect(screen, self.color, rect, width=3, border_radius=10)
        draw_arrow(screen, self.x, self.y, self.direction, size=40, color=(255,255,255))

class Note:
    def __init__(self, x, target_y, direction, speed=5, spawn_y=None):
        self.x = x
        self.target_y = target_y
        self.y = spawn_y if spawn_y is not None else target_y + 500
        self.direction = direction
        self.speed = speed
        self.color = ARROW_COLORS[direction]
        self.size = 60
        self.active = True

    def update(self):
        self.y -= self.speed
        if self.y < self.target_y - 100:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=8)
        pygame.draw.rect(screen, self.color, rect, width=3, border_radius=8)
        draw_arrow(screen, self.x, self.y, self.direction, size=40, color=(255,255,255))

class HealthBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player_health = 50.0
        self.opponent_health = 50.0
        self.face_size = 38
        self.player_face = self._create_face((50, 255, 50))
        self.opponent_face = self._create_face((255, 50, 50))

    def _create_face(self, color):
        surf = pygame.Surface((self.face_size, self.face_size), pygame.SRCALPHA)
        cx = self.face_size // 2
        cy = self.face_size // 2
        pygame.draw.circle(surf, color, (cx, cy), cx)
        eye_y = cy - 6
        pygame.draw.circle(surf, (255,255,255), (cx - 8, eye_y), 4)
        pygame.draw.circle(surf, (255,255,255), (cx + 8, eye_y), 4)
        pygame.draw.circle(surf, (0,0,0), (cx - 8, eye_y), 2)
        pygame.draw.circle(surf, (0,0,0), (cx + 8, eye_y), 2)
        mouth_y = cy + 10
        pygame.draw.arc(surf, (255,255,255), (cx - 6, mouth_y - 4, 12, 10), 0, math.pi, 2)
        return surf

    def update(self, player_delta, opponent_delta):
        self.player_health = max(0, min(100, self.player_health + player_delta - opponent_delta))
        self.opponent_health = 100 - self.player_health

    def draw(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), (self.x, self.y, self.width, self.height), border_radius=8)

        player_ratio = self.player_health / 100.0
        boundary_x = self.x + self.width * (1.0 - player_ratio)

        opp_width = boundary_x - self.x
        player_width = (self.x + self.width) - boundary_x

        if opp_width > 0:
            pygame.draw.rect(screen, (255, 50, 50),
                             (self.x, self.y, opp_width, self.height),
                             border_top_left_radius=8, border_bottom_left_radius=8)

        if player_width > 0:
            pygame.draw.rect(screen, (50, 255, 50),
                             (boundary_x, self.y, player_width, self.height),
                             border_top_right_radius=8, border_bottom_right_radius=8)

        if self.opponent_health > 0:
            opp_icon_x = boundary_x - self.face_size
            opp_icon_x = max(self.x - self.face_size//2, min(opp_icon_x, self.x + self.width - self.face_size//2))
            opp_icon_y = self.y + (self.height - self.face_size) // 2
            screen.blit(self.opponent_face, (opp_icon_x, opp_icon_y))

        if self.player_health > 0:
            player_icon_x = boundary_x
            player_icon_x = max(self.x - self.face_size//2, min(player_icon_x, self.x + self.width - self.face_size//2))
            player_icon_y = self.y + (self.height - self.face_size) // 2
            screen.blit(self.player_face, (player_icon_x, player_icon_y))

class JudgmentText:
    def __init__(self, text, x, y, color, duration=30):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.timer = duration

    def update(self):
        self.timer -= 1
        return self.timer <= 0

    def draw(self, screen, font):
        alpha = int(255 * self.timer / self.duration)
        surf = font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(self.x, self.y))
        screen.blit(surf, rect)

class BuffNote(Note):
    def __init__(self, x, target_y, direction, speed=5, spawn_y=None):
        super().__init__(x, target_y, direction, speed, spawn_y)
        self.glow_timer = 0

    def draw(self, screen):
        if not self.active:
            return
        self.glow_timer += 1
        glow_alpha = int(128 + 127 * math.sin(self.glow_timer * 0.1))
        glow_color = (255, 255, 0, glow_alpha)

        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        glow_rect = rect.inflate(10, 10)
        pygame.draw.rect(screen, glow_color, glow_rect, border_radius=12)

        super().draw(screen)
        pygame.draw.rect(screen, (255, 215, 0), rect, width=4, border_radius=8)

class Character:
    def __init__(self, x, y, model_name, target_height=200, is_player=True):
        self.x = x
        self.y = y
        self.model_name = model_name
        self.is_player = is_player
        self.anim_timer = 0
        self.current_pose = "idle"
        self.pose_timer = 0
        self.bpm = 120
        self.bob_offset = 0
        self.is_talking = False
        
        self.sprite = self._load_sprite(target_height)
        self.pose_sprites = {"idle": self.sprite, "left": self.sprite, "right": self.sprite, "up": self.sprite, "down": self.sprite}

    def _load_sprite(self, target_height):
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_filenames = [f"{self.model_name}_idle.png", f"{self.model_name}.png"]
        if self.model_name == "main_player":
            possible_filenames.extend(["image_748186.png", "8fab79d3-2534-4db0-9818-3ce60dd608fb.png"])
        elif self.model_name == "sub_girlfriend":
            possible_filenames.extend(["image_7481ca.png", "06ecd866-d078-4c4f-af0d-0dba66208cad.png"])
        elif self.model_name == "boss_char":
            possible_filenames.extend(["image_748205.png", "2ae098fa-ebbc-4148-9a20-e5b7f680cfdd.png"])

        possible_dirs = [
            os.path.join(current_script_dir, "images", "characters"),
            os.path.join(current_script_dir, "assets", "images", "characters"),
            current_script_dir
        ]
        
        for folder in possible_dirs:
            for fname in possible_filenames:
                filepath = os.path.join(folder, fname)
                if os.path.exists(filepath):
                    try:
                        sprite = pygame.image.load(filepath).convert_alpha()
                        orig_w, orig_h = sprite.get_size()
                        ratio = target_height / orig_h
                        print(f"[THÀNH CÔNG] Nhân vật '{self.model_name}' nhận diện tại: {filepath}")
                        return pygame.transform.scale(sprite, (int(orig_w * ratio), target_height))
                    except Exception as e:
                        print(f"Lỗi đọc dữ liệu ảnh {filepath}: {e}")
                        
        print(f"[THẤT BẠI] Không tìm thấy ảnh cho nhân vật: {self.model_name}")
        placeholder = pygame.Surface((100, target_height), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (100, 100, 100, 150), (0, 0, 100, target_height), border_radius=15)
        return placeholder

    def set_pose(self, pose):
        pose = pose.lower()
        if pose in self.pose_sprites:
            self.current_pose = pose
            self.pose_timer = 15

    def update(self, dt):
        beat_interval = 60 / self.bpm * 30
        self.anim_timer += 1
        if self.is_talking:
            self.bob_offset = math.sin(self.anim_timer / (beat_interval * 0.4) * 2 * math.pi) * 15
        else:
            self.bob_offset = math.sin(self.anim_timer / beat_interval * 2 * math.pi) * 8
        if self.pose_timer > 0:
            self.pose_timer -= 1
        else:
            self.current_pose = "idle"

    def draw(self, screen):
        current_sprite = self.pose_sprites.get(self.current_pose, self.sprite)
        if not self.is_player:
            current_sprite = pygame.transform.flip(current_sprite, True, False)
        spr_w, spr_h = current_sprite.get_size()
        screen.blit(current_sprite, (self.x - spr_w // 2, self.y - spr_h + self.bob_offset))


class DialogueBox:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.dialogues = []
        self.current_index = 0
        self.visible_text = ""
        self.char_index = 0
        self.text_speed = 2
        self.speed_counter = 0
        self.active = False
        self.callback = None

    def start_dialogue(self, dialogue_list, callback=None):
        self.dialogues = dialogue_list
        self.current_index = 0
        self.char_index = 0
        self.visible_text = ""
        self.active = True
        self.callback = callback
        self._update_speaker()

    def _update_speaker(self):
        if self.current_index < len(self.dialogues):
            speaker = self.dialogues[self.current_index].get("speaker")
            if speaker:
                speaker.is_talking = True

    def update(self, sound_manager):
        if not self.active or self.current_index >= len(self.dialogues):
            return
        current_data = self.dialogues[self.current_index]
        full_text = current_data["text"]
        speaker = current_data.get("speaker")

        if self.char_index < len(full_text):
            self.speed_counter += 1
            if self.speed_counter >= self.text_speed:
                self.speed_counter = 0
                self.visible_text += full_text[self.char_index]
                self.char_index += 1
                if self.char_index % 3 == 0:
                    sound_manager.play_sfx("text_click", volume=0.2)
        else:
            if speaker:
                speaker.is_talking = False

    def next_sentence(self):
        if not self.active:
            return
        current_data = self.dialogues[self.current_index]
        full_text = current_data["text"]
        speaker = current_data.get("speaker")

        if self.char_index < len(full_text):
            self.visible_text = full_text
            self.char_index = len(full_text)
            if speaker:
                speaker.is_talking = False
            return

        if speaker:
            speaker.is_talking = False
        self.current_index += 1
        self.char_index = 0
        self.visible_text = ""

        if self.current_index >= len(self.dialogues):
            self.active = False
            if self.callback:
                self.callback()
        else:
            self._update_speaker()

    def draw(self, screen):
        if not self.active or self.current_index >= len(self.dialogues):
            return
        # Vẽ nền và viền
        pygame.draw.rect(screen, (10, 10, 30, 220), self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 0), self.rect, width=3, border_radius=10)

        current_data = self.dialogues[self.current_index]
        name = current_data.get("name", "???")
        color = current_data.get("color", (255, 255, 255))
        name_surf = self.font.render(name, True, color)
        screen.blit(name_surf, (self.rect.x + 20, self.rect.y + 15))

        text_surf = self.font.render(self.visible_text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + 20, self.rect.y + 55))

        # Hướng dẫn bấm phím
        tip_font = pygame.font.Font(None, 20)
        tip_surf = tip_font.render("[ENTER/SPACE] De tiep tuc", True, (150, 150, 150))
        screen.blit(tip_surf, (self.rect.right - tip_surf.get_width() - 20, self.rect.bottom - 25))