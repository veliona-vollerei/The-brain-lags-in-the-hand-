import pygame
import random
import sys
from game_objects import Receptor, Note, HealthBar, Character, JudgmentText
from utils import cv2_to_pygame

def run_vs_gameplay(screen, clock, font, big_font, huge_font, network, settings, tracker, classifier):
    SCREEN_W, SCREEN_H = settings['resolution']
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    background = pygame.Surface((SCREEN_W, SCREEN_H))
    background.fill((15, 15, 30))

    # Lấy tên từ network (đã được thiết lập khi kết nối)
    player_name = network.player_name if network.player_name else "Player"
    opponent_name = network.opponent_name if network.opponent_name else "Opponent"

    RECEPTOR_Y = 150
    spacing = 80

    # Người chơi bên trái (self)
    left_receptors = {}
    left_center_x = 280
    for i, d in enumerate(["LEFT", "DOWN", "UP", "RIGHT"]):
        x = left_center_x + (i - 1.5) * spacing
        left_receptors[d] = Receptor(x, RECEPTOR_Y, d)

    # Đối thủ bên phải
    right_receptors = {}
    right_center_x = SCREEN_W - 280
    for i, d in enumerate(["LEFT", "DOWN", "UP", "RIGHT"]):
        x = right_center_x + (i - 1.5) * spacing
        right_receptors[d] = Receptor(x, RECEPTOR_Y, d)

    # Khởi tạo Character với model_name phù hợp
    left_char = Character(200, SCREEN_H - 250, "main_player", target_height=100, is_player=True)
    right_char = Character(SCREEN_W - 200, SCREEN_H - 250, "boss_char", target_height=100, is_player=False)

    health_bar = HealthBar(SCREEN_W//2 - 300, SCREEN_H - 80, 600, 30)

    left_notes = []
    right_notes = []

    spawn_timer = 0
    SPAWN_INTERVAL = 40
    score = 0
    combo = 0
    max_combo = 0
    judgments = []
    game_over = False
    game_result = None

    my_gesture = "NONE"
    opponent_gesture = "NONE"

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network.close()
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                network.close()
                return "menu"

        # Lấy cử chỉ của mình
        landmarks, handedness = tracker.get_landmarks()
        if landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            my_gesture = classifier.classify(landmarks[hand_idx])

        # Gửi cử chỉ của mình cho đối thủ qua host
        network.send_data(my_gesture)
        opp = network.get_opponent_action()
        if opp is not None:
            opponent_gesture = opp

        # Spawn note (giống nhau cho cả 2 bên)
        spawn_timer += 1
        if spawn_timer % SPAWN_INTERVAL == 0:
            d = random.choice(["LEFT", "DOWN", "UP", "RIGHT"])
            left_notes.append(Note(left_receptors[d].x, RECEPTOR_Y, d, speed=4, spawn_y=RECEPTOR_Y+400))
            right_notes.append(Note(right_receptors[d].x, RECEPTOR_Y, d, speed=4, spawn_y=RECEPTOR_Y+400))

        # Xử lý note bên trái (của người chơi)
        for note in left_notes[:]:
            note.update()
            if note.y < RECEPTOR_Y - 30:
                if not game_over:
                    health_bar.update(0, 2)
                    combo = 0
                    judgments.append(JudgmentText("MISS", note.x, RECEPTOR_Y - 60, (255,50,50), 40))
                left_notes.remove(note)
                continue
            if note.y <= RECEPTOR_Y + 25 and note.y >= RECEPTOR_Y - 25:
                if my_gesture == note.direction:
                    score += 100
                    combo += 1
                    if combo > max_combo:
                        max_combo = combo
                    health_bar.update(2, 0)
                    judgments.append(JudgmentText("PERFECT", note.x, RECEPTOR_Y - 60, (0,255,255), 40))
                else:
                    health_bar.update(0, 2)
                    combo = 0
                    judgments.append(JudgmentText("WRONG", note.x, RECEPTOR_Y - 60, (255,150,0), 40))
                left_notes.remove(note)

        # Xử lý note bên phải (chỉ remove, không tính điểm)
        for note in right_notes[:]:
            note.update()
            if note.y < RECEPTOR_Y - 30 or (note.y <= RECEPTOR_Y + 25 and note.y >= RECEPTOR_Y - 25):
                right_notes.remove(note)

        # Kiểm tra kết thúc
        if health_bar.player_health <= 0:
            game_over = True
            game_result = "LOSE"
        elif health_bar.player_health >= 100:
            game_over = True
            game_result = "WIN"

        # Vẽ
        screen.blit(background, (0,0))
        for rec in left_receptors.values():
            rec.draw(screen)
        for rec in right_receptors.values():
            rec.draw(screen)
        for note in left_notes:
            note.draw(screen)
        for note in right_notes:
            note.draw(screen)
        left_char.draw(screen)
        right_char.draw(screen)
        health_bar.draw(screen)

        for j in judgments[:]:
            if j.update():
                judgments.remove(j)
            else:
                j.draw(screen, big_font)

        screen.blit(font.render(f"{player_name}: {score}", True, (255,255,255)), (20, 20))
        screen.blit(font.render(f"{opponent_name}: ???", True, (255,255,255)), (SCREEN_W-300, 20))
        screen.blit(font.render(f"Combo: {combo} (Max: {max_combo})", True, (255,255,100)), (20, 55))
        screen.blit(font.render(f"Your Gesture: {my_gesture}", True, (200,200,200)), (20, SCREEN_H-40))
        screen.blit(font.render(f"Opponent Gesture: {opponent_gesture}", True, (200,200,200)), (SCREEN_W-350, SCREEN_H-40))

        debug_bgr = tracker.get_debug_frame()
        if debug_bgr is not None:
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(128,96))
            screen.blit(debug_surf, (SCREEN_W-140,20))

        if game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            if game_result == "WIN":
                text = huge_font.render("VICTORY!", True, (0,255,0))
            else:
                text = huge_font.render("DEFEAT!", True, (255,50,50))
            screen.blit(text, (SCREEN_W//2 - text.get_width()//2, SCREEN_H//2-80))
            screen.blit(font.render("ESC to exit", True, (255,255,255)), (SCREEN_W//2-80, SCREEN_H//2+20))

        pygame.display.flip()

    return "menu"