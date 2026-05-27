import pygame
import sys
import random
from hand_tracker import HandTracker
from game_objects import Receptor, Note, HealthBar, Character, JudgmentText, BuffNote, DialogueBox
from ai_gesture_classifier import AIGestureClassifier
from utils import load_random_background, cv2_to_pygame
from menu import Menu
from buff_system import get_random_buff, get_random_debuff, ActiveBuff
from minigame_millionaire import run_minigame
from minigame_flappy import run_flappy_minigame
from minigame_pictionary import PictionaryGame
from minigame_king_vietnamese import KingVietnameseGame
from sound_manager import SoundManager
from network import Network
from game_vs import run_vs_gameplay

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BG_COLOR = (15, 15, 30)
RED = (255, 50, 50)

# ==============================================================================
# HÀM CHẠY CỐT TRUYỆN ĐIỆN ẢNH (CINEMATIC SCROLL)
# ==============================================================================
def run_story_intro(screen, clock, font, big_font, screen_w, screen_h):
    story_text = [
       "NĂM 2026...",
        "",
        "xuất hiện 1 women làm điên đảo khắp thế giới.",
        "women phải lòng anh main (người chơi), nhưng vẫn có",
        "",
        "những kẻ vẫn muốn được độc chiếm lấy wonman đó.",
        "su thế hiện tai của thế giới là giải quyết mọi",
        "vấn đề bằng âm nhạc.",
        "chính vì thế mà có rất nhiều kẻ thù xuất hiện,",
        "thách đấu với main",
        "",
        "Chi co minh ban chien dau,"
        "bạn phải chiến một mình"
        "và women (GIRLFRIEND) chỉ cổ vũ, không can thiệp vào trận đấu",
        "",
        "bạn phải chiến thắng tất cả các kẻ thù,",
        "để bảo vệ em ghẹ của mình",
        "",
        "[ Nhan ENTER hoac SPACE de bo qua ]"
    ]
    
    rendered_lines = [big_font.render(line, True, (200, 200, 255)) for line in story_text]
    rendered_lines[-1] = font.render(story_text[-1], True, (150, 150, 150))
    
    y_offset = screen_h
    scroll_speed = 1.2
    
    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    running = False
        
        screen.fill((5, 5, 10))
        current_y = y_offset
        for i, surf in enumerate(rendered_lines):
            rect = surf.get_rect(center=(screen_w // 2, current_y))
            screen.blit(surf, rect)
            if i == len(rendered_lines) - 2:
                current_y += 100
            else:
                current_y += 60
        y_offset -= scroll_speed
        
        pygame.draw.rect(screen, BLACK, (0, 0, screen_w, 80))
        pygame.draw.rect(screen, BLACK, (0, screen_h - 80, screen_w, 80))
        
        pygame.display.flip()
        if current_y < -50:
            running = False

def countdown_before_resume(screen, clock, game_bg, screen_w, screen_h, huge_font, tracker):
    for count in range(3, 0, -1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        screen.blit(game_bg, (0, 0))
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        text = huge_font.render(str(count), True, WHITE)
        screen.blit(text, (screen_w//2 - text.get_width()//2, screen_h//2 - text.get_height()//2))

        debug_bgr = tracker.get_debug_frame()
        if debug_bgr is not None:
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(int(640*0.2), int(480*0.2)))
            screen.blit(debug_surf, (screen_w - 160, 20))

        pygame.display.flip()
        clock.tick(1)

def run_gameplay(screen, clock, font, big_font, huge_font, chapter_config, settings, sound_manager):
    SCREEN_W, SCREEN_H = settings['resolution']
    if screen.get_size() != (SCREEN_W, SCREEN_H):
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    bg_folder = "backgrounds"
    background = load_random_background(bg_folder, (SCREEN_W, SCREEN_H))

    CAM_W, CAM_H = 640, 480
    tracker = HandTracker(width=CAM_W, height=CAM_H, alpha=0.3)
    tracker.start()
    classifier = AIGestureClassifier(stable_frames=4)

    difficulty = chapter_config.get('difficulty', 1)
    base_speed = chapter_config.get('base_speed', 3)

    if difficulty == 1:
        def get_speed(elapsed_frames):
            return base_speed
    elif difficulty == 2:
        max_speed = base_speed * 2.5
        increase_rate = 0.002
        def get_speed(elapsed_frames):
            return min(base_speed + elapsed_frames * increase_rate, max_speed)
    else:
        increase_rate = 0.003
        def get_speed(elapsed_frames):
            return base_speed + elapsed_frames * increase_rate

    RECEPTOR_Y = 150
    spacing = 80
    opp_center_x = 280
    opp_receptors = {}
    for i, d in enumerate(["LEFT", "DOWN", "UP", "RIGHT"]):
        x = opp_center_x + (i - 1.5) * spacing
        opp_receptors[d] = Receptor(x, RECEPTOR_Y, d)

    player_center_x = SCREEN_W - 280
    player_receptors = {}
    for i, d in enumerate(["LEFT", "DOWN", "UP", "RIGHT"]):
        x = player_center_x + (i - 1.5) * spacing
        player_receptors[d] = Receptor(x, RECEPTOR_Y, d)

    opponent_char = Character(200, SCREEN_H - 250, "boss_char", target_height=100, is_player=False)
    player_char = Character(SCREEN_W - 200, SCREEN_H - 250, "main_player", target_height=100, is_player=True)
    girlfriend = Character(SCREEN_W // 2, SCREEN_H - 300, "sub_girlfriend", target_height=150, is_player=False)

    health_bar = HealthBar(SCREEN_W//2 - 300, SCREEN_H - 80, 600, 30)

    opp_notes = []
    player_notes = []
    spawn_timer = 0
    SPAWN_INTERVAL = max(20, int(40 - base_speed * 3))

    score = 0
    combo = 0
    max_combo = 0
    judgments = []

    auto_play = False
    game_over = False
    game_result = None
    elapsed_frames = 0

    active_buffs = []
    opponent_buffs = []
    buff_spawn_timer = 0
    BUFF_SPAWN_INTERVAL = 600
    combo_buff_triggered = False
    combo_debuff_triggered = False

    in_minigame = False
    minigame_result = None
    game_background = None

    game_state = {"status": "INTRO_DIALOGUE"}
    def set_state_playing():
        game_state["status"] = "PLAYING"
        try: pygame.mixer.music.set_volume(0.5)
        except: pass

    dialogue_box = DialogueBox(SCREEN_W//2 - 400, SCREEN_H - 230, 800, 130, font)

    intro_script = [
        {"speaker": opponent_char, "name": "BOSS", "color": RED, "text": "Nha cua ngươi se la bai tha ma cua am nhac!! Ready?!"},
        {"speaker": player_char, "name": "MAIN", "color": (50, 150, 255), "text": "Hay xem doi tay ma thuat cua ta day, dung gáy som!"},
        {"speaker": girlfriend, "name": "GIRLFRIEND", "color": (255, 105, 180), "text": "Co len anh oi, dung de han huong dan tran dau!"}
    ]
    dialogue_box.start_dialogue(intro_script, callback=set_state_playing)

    show_tutorial = chapter_config.get('name', '').startswith('Chapter 1')
    waiting_for_start = show_tutorial
    tutorial_text = [
        "HUONG DAN:",
        "👍 Ngon cai -> UP",
        "☝️ 1 ngon tay -> DOWN",
        "✌️ 2 ngon -> LEFT",
        "🖐️ Xoe tay -> RIGHT",
        "✊ Nam tay -> NONE",
        "",
        "Note vang phat sang la Buff!",
        "An dung de vao mini game nhan buff!",
        "",
        "Nhan ENTER de bat dau!"
    ]
    climax_triggered = False
    gesture = "NONE"

    running = True
    while running:
        # --- TUTORIAL ---
        if waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    tracker.stop()
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting_for_start = False
                    if event.key == pygame.K_ESCAPE:
                        tracker.stop()
                        return "menu"
            screen.fill(BG_COLOR)
            y = 100
            for line in tutorial_text:
                text = font.render(line, True, WHITE)
                screen.blit(text, (SCREEN_W//2 - text.get_width()//2, y))
                y += 35
            debug_bgr = tracker.get_debug_frame()
            if debug_bgr is not None:
                debug_surf = cv2_to_pygame(debug_bgr, target_size=(int(CAM_W*0.2), int(CAM_H*0.2)))
                screen.blit(debug_surf, (SCREEN_W - 160, 20))
            pygame.display.flip()
            clock.tick(30)
            continue

        # --- MINI GAME ---
        if in_minigame:
            if game_background is None:
                game_background = screen.copy()
            mini_game_type = random.choice(["millionaire", "flappy", "pictionary", "kingviet"])
            if mini_game_type == "millionaire":
                minigame_result = run_minigame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier, game_background)
            elif mini_game_type == "flappy":
                minigame_result = run_flappy_minigame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier, game_background, sound_manager)
            elif mini_game_type == "pictionary":
                pg = PictionaryGame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier)
                minigame_result = pg.run()
            else:  # kingviet
                kg = KingVietnameseGame(screen, clock, SCREEN_W, SCREEN_H, font, big_font, tracker, classifier)
                minigame_result = kg.run()
            in_minigame = False
            if minigame_result:
                sound_manager.play_sfx("buff")
                buff = get_random_buff()
                active_buffs.append(ActiveBuff(buff))
                judgments.append(JudgmentText(f"Buff: {buff.name}", SCREEN_W//2, SCREEN_H//2, buff.color, 180))
                if random.random() < 0.3:
                    debuff = get_random_debuff()
                    opponent_buffs.append(ActiveBuff(debuff))
                    judgments.append(JudgmentText(f"Debuff: {debuff.name}", SCREEN_W//2, SCREEN_H//2 - 80, debuff.color, 180))
            else:
                sound_manager.play_sfx("miss")
                judgments.append(JudgmentText("Khong nhan duoc buff!", SCREEN_W//2, SCREEN_H//2, RED, 180))
            countdown_before_resume(screen, clock, game_background, SCREEN_W, SCREEN_H, huge_font, tracker)
            game_background = None
            continue

        dt = clock.tick(settings['fps']) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tracker.stop()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    tracker.stop()
                    return "menu"
                if dialogue_box.active and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    dialogue_box.next_sentence()
                    continue
                if event.key == pygame.K_a:
                    auto_play = not auto_play
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    game_result = None
                    health_bar.player_health = 50
                    health_bar.opponent_health = 50
                    score = 0
                    combo = 0
                    max_combo = 0
                    opp_notes.clear()
                    player_notes.clear()
                    judgments.clear()
                    active_buffs.clear()
                    opponent_buffs.clear()
                    auto_play = False
                    elapsed_frames = 0
                    combo_buff_triggered = False
                    combo_debuff_triggered = False
                    climax_triggered = False
                    game_state["status"] = "INTRO_DIALOGUE"
                    dialogue_box.start_dialogue(intro_script, callback=set_state_playing)

        if dialogue_box.active:
            dialogue_box.update(sound_manager)

        current_state = game_state["status"]

        if current_state == "PLAYING" and not game_over:
            if not climax_triggered and (health_bar.player_health <= 25 or health_bar.player_health >= 75):
                climax_triggered = True
                try: pygame.mixer.music.set_volume(0.1)
                except: pass
                if health_bar.player_health <= 25:
                    c_script = [{"speaker": opponent_char, "name": "BOSS", "color": RED, "text": "Kha nang cua ngươi chi den the thoi sao? Chuan bi thua cuoc di!"}]
                else:
                    c_script = [{"speaker": player_char, "name": "MAIN", "color": (50, 150, 255), "text": "Nhip dieu tran nay hoan toan thuoc ve ta! Sap xong doi ngươi roi!"}]
                game_state["status"] = "CLIMAX_DIALOGUE"
                dialogue_box.start_dialogue(c_script, callback=set_state_playing)
                continue

        for buff in active_buffs[:]:
            buff.update(dt)
            if not buff.active:
                active_buffs.remove(buff)

        speed_multiplier = 1.0
        is_auto_perfect = False
        is_invincible = False
        score_multiplier = 1
        is_combo_shield = False
        for buff in active_buffs:
            if buff.effect_type == "slow_motion":
                speed_multiplier = buff.effect_value
            elif buff.effect_type == "auto_perfect":
                is_auto_perfect = True
            elif buff.effect_type == "invincible":
                is_invincible = True
            elif buff.effect_type == "double_score":
                score_multiplier = buff.effect_value
            elif buff.effect_type == "combo_shield":
                is_combo_shield = True

        opponent_speed_mult = 1.0
        opponent_fog_alpha = 0
        opponent_auto_miss = False
        opponent_invert = False
        opponent_reflect = False
        for debuff in opponent_buffs:
            if debuff.effect_type == "opponent_speed_up":
                opponent_speed_mult = debuff.effect_value
            elif debuff.effect_type == "opponent_fog":
                opponent_fog_alpha = debuff.effect_value
            elif debuff.effect_type == "opponent_auto_miss":
                opponent_auto_miss = True
            elif debuff.effect_type == "opponent_freeze":
                opponent_speed_mult = debuff.effect_value
            elif debuff.effect_type == "opponent_invert":
                opponent_invert = True
            elif debuff.effect_type == "opponent_reflect":
                opponent_reflect = True

        elapsed_frames += 1
        current_speed = get_speed(elapsed_frames) * speed_multiplier

        landmarks, handedness = tracker.get_landmarks()
        gesture = "NONE"
        if not auto_play and landmarks and handedness:
            hand_idx = 0
            for i, h in enumerate(handedness):
                if h.classification[0].label == "Right":
                    hand_idx = i
                    break
            gesture = classifier.classify(landmarks[hand_idx])

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BG_COLOR)

        debug_bgr = tracker.get_debug_frame()
        if debug_bgr is not None:
            debug_surf = cv2_to_pygame(debug_bgr, target_size=(int(CAM_W*0.2), int(CAM_H*0.2)))
            screen.blit(debug_surf, (SCREEN_W - 160, 20))

        if not game_over and current_state == "PLAYING":
            spawn_timer += 1
            buff_spawn_timer += 1
            if spawn_timer % SPAWN_INTERVAL == 0:
                d = random.choice(["LEFT", "DOWN", "UP", "RIGHT"])
                x = opp_receptors[d].x
                opp_speed = current_speed * opponent_speed_mult
                opp_notes.append(Note(x, RECEPTOR_Y, d, speed=opp_speed, spawn_y=RECEPTOR_Y + 400))

            if spawn_timer % (SPAWN_INTERVAL + 10) == 5:
                d = random.choice(["LEFT", "DOWN", "UP", "RIGHT"])
                x = player_receptors[d].x
                player_notes.append(Note(x, RECEPTOR_Y, d, speed=current_speed, spawn_y=RECEPTOR_Y + 400))

            if buff_spawn_timer >= BUFF_SPAWN_INTERVAL:
                buff_spawn_timer = 0
                d = random.choice(["LEFT", "DOWN", "UP", "RIGHT"])
                x = player_receptors[d].x
                player_notes.append(BuffNote(x, RECEPTOR_Y, d, speed=current_speed, spawn_y=RECEPTOR_Y + 400))

            if combo > 0 and combo % 30 == 0 and not combo_buff_triggered:
                d = random.choice(["LEFT", "DOWN", "UP", "RIGHT"])
                x = player_receptors[d].x
                player_notes.append(BuffNote(x, RECEPTOR_Y, d, speed=current_speed, spawn_y=RECEPTOR_Y + 400))
                combo_buff_triggered = True
            elif combo % 30 != 0:
                combo_buff_triggered = False

            if combo > 0 and combo % 50 == 0 and not combo_debuff_triggered:
                debuff = get_random_debuff()
                opponent_buffs.append(ActiveBuff(debuff))
                judgments.append(JudgmentText(f"Debuff: {debuff.name}", SCREEN_W//2, SCREEN_H//2 - 80, debuff.color, 180))
                combo_debuff_triggered = True
            elif combo % 50 != 0:
                combo_debuff_triggered = False

            for note in opp_notes[:]:
                note.update()
                if opponent_invert:
                    note.y = 2 * RECEPTOR_Y - note.y
                if not note.active:
                    opp_notes.remove(note)
                    continue
                if note.y <= RECEPTOR_Y + 20 and note.y >= RECEPTOR_Y - 20:
                    if opponent_auto_miss:
                        health_bar.update(0, 0)
                    elif opponent_reflect:
                        health_bar.update(0.5, 0)
                    else:
                        health_bar.update(0, 0.5)
                    opponent_char.set_pose(note.direction)
                    opp_notes.remove(note)

            for note in player_notes[:]:
                note.update()
                if note.y < RECEPTOR_Y - 30:
                    if not auto_play:
                        if not is_invincible and not is_combo_shield:
                            combo = 0
                            health_bar.update(0, 2)
                            sound_manager.play_sfx("miss")
                        elif is_combo_shield:
                            pass
                        judgments.append(JudgmentText("MISS", note.x, RECEPTOR_Y - 60, RED, 40))
                    player_notes.remove(note)
                    continue

                if note.y <= RECEPTOR_Y + 25 and note.y >= RECEPTOR_Y - 25:
                    hit = False
                    is_buff_note = isinstance(note, BuffNote)

                    if auto_play or is_auto_perfect:
                        pts, judge = 100, "PERFECT"
                        hp_gain = 2
                        color = (0, 255, 255)
                        hit = True
                    elif gesture == note.direction:
                        dist = abs(note.y - RECEPTOR_Y)
                        if dist < 10:
                            pts, judge = 100, "PERFECT"
                            hp_gain = 2
                            color = (0, 255, 255)
                        elif dist < 20:
                            pts, judge = 70, "GOOD"
                            hp_gain = 1
                            color = (0, 255, 0)
                        else:
                            pts, judge = 30, "NON"
                            hp_gain = 0.3
                            color = (255, 150, 0)
                        hit = True

                    if hit:
                        if is_buff_note:
                            sound_manager.play_sfx("hit")
                            game_background = screen.copy()
                            in_minigame = True
                            player_notes.remove(note)
                            continue

                        sound_manager.play_sfx("hit")
                        pts *= score_multiplier
                        score += pts
                        combo += 1
                        if combo > max_combo:
                            max_combo = combo
                        health_bar.update(hp_gain, 0)
                        player_char.set_pose(note.direction)
                        judgments.append(JudgmentText(f"{judge} +{pts}", note.x, RECEPTOR_Y - 60, color, 40))
                        player_notes.remove(note)

            for buff in active_buffs[:]:
                if buff.effect_type == "hp_regen_percent" and not buff.shield_used:
                    heal_amount = health_bar.player_health * buff.effect_value / 100
                    health_bar.player_health = min(100, health_bar.player_health + heal_amount)
                    buff.shield_used = True

            opponent_char.update(30)
            player_char.update(30)
            girlfriend.update(30)

            for j in judgments[:]:
                if j.update():
                    judgments.remove(j)

            if health_bar.player_health >= 100:
                game_over = True
                try: pygame.mixer.music.set_volume(0.1)
                except: pass
                game_result = "WIN"
                out_script = [{"speaker": opponent_char, "name": "BOSS", "color": RED, "text": "Khong... Nhịp dieu cua ta da hoan toan tan ra!"}]
                game_state["status"] = "OUTRO_DIALOGUE"
                def set_state_finished(): game_state["status"] = "FINISHED"
                dialogue_box.start_dialogue(out_script, callback=set_state_finished)
            elif health_bar.player_health <= 0:
                game_over = True
                try: pygame.mixer.music.set_volume(0.1)
                except: pass
                game_result = "LOSE"
                out_script = [{"speaker": player_char, "name": "MAIN", "color": (50, 150, 255), "text": "Uoc gi... tay cua minh nhanh hon... Ta da guc nga..."}]
                game_state["status"] = "OUTRO_DIALOGUE"
                def set_state_finished(): game_state["status"] = "FINISHED"
                dialogue_box.start_dialogue(out_script, callback=set_state_finished)

        for rec in opp_receptors.values():
            rec.draw(screen)
        for rec in player_receptors.values():
            rec.draw(screen)

        for note in opp_notes:
            if opponent_fog_alpha > 0:
                note_surf = pygame.Surface((note.size, note.size), pygame.SRCALPHA)
                note.draw(note_surf)
                note_surf.set_alpha(int(255 * (1 - opponent_fog_alpha)))
                screen.blit(note_surf, (note.x - note.size//2, note.y - note.size//2))
            else:
                note.draw(screen)

        for note in player_notes:
            note.draw(screen)

        opponent_char.draw(screen)
        player_char.draw(screen)
        girlfriend.draw(screen)
        health_bar.draw(screen)

        for j in judgments:
            j.draw(screen, big_font)

        y_buff = 20
        for buff in active_buffs:
            b_text = font.render(f"{buff.buff.icon_char} {buff.buff.name}: {buff.remaining_time:.1f}s", True, buff.buff.color)
            screen.blit(b_text, (SCREEN_W - 300, y_buff))
            y_buff += 25

        for debuff in opponent_buffs:
            d_text = font.render(f"{debuff.buff.icon_char} Doi thu: {debuff.buff.name} {debuff.remaining_time:.1f}s", True, debuff.buff.color)
            screen.blit(d_text, (SCREEN_W - 500, y_buff))
            y_buff += 25

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        combo_text = font.render(f"Combo: {combo}  (Max: {max_combo})", True, (255, 255, 100))
        screen.blit(combo_text, (20, 55))
        speed_text = font.render(f"Speed: {current_speed:.1f}", True, GRAY)
        screen.blit(speed_text, (20, SCREEN_H - 60))

        if auto_play:
            auto_text = font.render("AUTO PLAY (A to toggle)", True, (0, 255, 255))
            screen.blit(auto_text, (SCREEN_W//2 - 120, 20))
        else:
            gest_text = font.render(f"Gesture: {gesture}", True, (200, 200, 200))
            screen.blit(gest_text, (20, SCREEN_H - 40))

        if dialogue_box.active:
            dialogue_box.draw(screen)

        if game_over and game_state["status"] == "FINISHED":
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            if game_result == "WIN":
                result_text = huge_font.render("YOU WIN!", True, (0, 255, 0))
            else:
                result_text = huge_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(result_text, (SCREEN_W//2 - result_text.get_width()//2, SCREEN_H//2 - 80))
            screen.blit(font.render("Nhan R de choi lai | ESC de thoat", True, WHITE), (SCREEN_W//2 - 180, SCREEN_H//2 + 20))

        pygame.display.flip()

    tracker.stop()
    return "menu"

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1360, 768
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("The brain lags in the hand")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 56)
    huge_font = pygame.font.Font(None, 80)

    sound_manager = SoundManager()
    sound_manager.load_sfx("hit", "hit.wav")
    sound_manager.load_sfx("miss", "miss.wav")
    sound_manager.load_sfx("buff", "buff.wav")
    sound_manager.load_sfx("jump", "jump.wav")
    sound_manager.load_sfx("text_click", "text_click.wav")

    menu = Menu(screen, clock, font, big_font, huge_font)
    settings = {
        'volume': 0.7,
        'fps': 60,
        'resolution': (1360, 768)
    }

    current_state = "intro_scroll"
    current_network = None
    current_player_name = "Player1"
    current_opponent_name = "Player2"

    while True:
        if current_state in ["main", "play", "settings", "story", "freeplay", "intro_scroll"]:
            sound_manager.play_bgm("01 Menu Theme.mp3", volume=0.4)

        if current_state == "intro_scroll":
            run_story_intro(screen, clock, font, big_font, SCREEN_W, SCREEN_H)
            current_state = "main"
        elif current_state == "main":
            result = menu.main_menu()
            if result == "play":
                current_state = "play"
            elif result == "settings":
                current_state = "settings"
        elif current_state == "play":
            result = menu.play_menu()
            if result == "story":
                current_state = "story"
            elif result == "freeplay":
                current_state = "freeplay"
            elif result == "versus":
                current_state = "versus"
            elif result == "main":
                current_state = "main"
        elif current_state == "story":
            result = menu.story_menu()
            if result == "start_game":
                sound_manager.play_bgm("01. Shootin’ Ropes (Pico Results Perfect Theme).mp3", volume=0.5)
                chapter = menu.selected_chapter
                run_gameplay(screen, clock, font, big_font, huge_font, chapter, settings, sound_manager)
                current_state = "main"
            elif result == "play":
                current_state = "play"
        elif current_state == "freeplay":
            result = menu.freeplay_menu()
            if result == "start_game":
                sound_manager.play_bgm("01. Shootin’ Ropes (Pico Results Perfect Theme).mp3", volume=0.5)
                chapter = menu.selected_chapter
                run_gameplay(screen, clock, font, big_font, huge_font, chapter, settings, sound_manager)
                current_state = "main"
            elif result == "play":
                current_state = "play"
        # main.py - bổ sung trong vòng lặp chính

        elif current_state == "versus":
            result = menu.versus_menu()
            if result == "play":
                current_state = "play"
            elif isinstance(result, tuple):
                if result[0] == "host":
                    _, room_code = result
                    network = Network()
                    if network.start_broadcast(room_code, "Host"):
                        current_network = network
                        current_state = "host_waiting"
                    else:
                        print("Không thể tạo phòng")
                        current_state = "play"
                elif result[0] == "join":
                    _, ip, room_code, player_name = result
                    network = Network()
                    if network.connect_to_server(ip, 5555, room_code, player_name):
                        current_network = network
                        current_state = "vs_game"
                    else:
                        print("Kết nối thất bại")
                        current_state = "play"
            elif result == "main":
                current_state = "main"

        elif current_state == "host_waiting":
            # Host chỉ chờ, hiển thị màn hình đen hoặc thông báo
            waiting = True
            while waiting and current_network and not current_network.host_game_ready:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        current_network.close()
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        waiting = False
                screen.fill((15,15,30))
                text = font.render("Đang chờ 2 người chơi kết nối... (ESC hủy)", True, WHITE)
                screen.blit(text, (SCREEN_W//2 - text.get_width()//2, SCREEN_H//2))
                pygame.display.flip()
                clock.tick(30)
            if current_network:
                current_network.close()
                current_network = None
            current_state = "main"

        elif current_state == "vs_game":
            # Client: chạy game đấu
            vs_tracker = HandTracker(width=640, height=480, alpha=0.3)
            vs_tracker.start()
            vs_classifier = AIGestureClassifier(stable_frames=4)
            # Cần lấy tên từ network (đã có trong network.player_name và network.opponent_name)
            # Nhưng trong game_vs.py ta sẽ truyền vào
            result = run_vs_gameplay(screen, clock, font, big_font, huge_font, current_network, settings, vs_tracker, vs_classifier)
            vs_tracker.stop()
            if current_network:
                current_network.close()
                current_network = None
            if result == "menu":
                current_state = "main"
            elif result == "quit":
                break
        elif current_state == "settings":
            result = menu.settings_menu()
            if result == "main":
                settings['volume'] = menu.volume
                settings['fps'] = menu.fps
                settings['resolution'] = menu.resolution
                current_state = "main"

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
