import pygame
import os

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            # MỞ RỘNG KÊNH ÂM THANH LÊN 32 (Mặc định chỉ có 8) ĐỂ CHỐNG VĂNG GAME
            pygame.mixer.set_num_channels(32) 
        except Exception as e:
            print(f"Lỗi khi khởi tạo mixer: {e}")
        self.sfx = {}
        self.current_bgm_path = None

    def load_sfx(self, name, filepath):
        if os.path.exists(filepath):
            try:
                self.sfx[name] = pygame.mixer.Sound(filepath)
            except Exception as e:
                print(f"Lỗi khi tải file âm thanh {filepath}: {e}")
        else:
            print(f"Cảnh báo: Không tìm thấy SFX tại {os.path.abspath(filepath)}")

    def play_sfx(self, name, volume=1.0):
        if name in self.sfx:
            try:
                self.sfx[name].set_volume(volume)
                self.sfx[name].play()
            except:
                pass # Bỏ qua nếu các kênh âm thanh đang bị kẹt

    def play_bgm(self, filepath, volume=0.5, loop=-1):
        if os.path.exists(filepath):
            if self.current_bgm_path != filepath:
                try:
                    pygame.mixer.music.load(filepath)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loop)
                    self.current_bgm_path = filepath
                except Exception as e:
                    print(f"Lỗi khi phát nhạc nền {filepath}: {e}")
        else:
            print(f"Cảnh báo: Không tìm thấy BGM tại {os.path.abspath(filepath)}")

    def stop_bgm(self):
        try:
            pygame.mixer.music.stop()
        except: pass
        self.current_bgm_path = None