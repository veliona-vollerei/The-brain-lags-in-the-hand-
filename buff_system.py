import random
import pygame

class Buff:
    def __init__(self, name, description, duration, effect_type, effect_value, color, icon_char, tier="common", is_debuff=False):
        self.name = name
        self.description = description
        self.duration = duration
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.color = color
        self.icon_char = icon_char
        self.tier = tier
        self.is_debuff = is_debuff

BUFF_COMMON = [
    Buff("Hoi Mau Nho", "Hoi 10% HP", 0, "hp_regen_percent", 10, (100, 255, 100), "💚", "common"),
    Buff("Tang Diem Nhe", "Nhan doi diem 5s", 5, "double_score", 2, (255, 255, 100), "⭐", "common"),
    Buff("Cham Nhe", "Giam 20% toc do 4s", 4, "slow_motion", 0.8, (150, 200, 255), "🐌", "common"),
    Buff("La Chan Yeu", "Bo qua miss 3s", 3, "invincible", 1, (180, 180, 255), "🛡️", "common"),
]

BUFF_RARE = [
    Buff("Hoi Mau Vua", "Hoi 25% HP", 0, "hp_regen_percent", 25, (255, 150, 150), "💖", "rare"),
    Buff("Tang Diem Manh", "Nhan 4 diem 5s", 5, "double_score", 4, (255, 200, 50), "🌟", "rare"),
    Buff("Cham Vua", "Giam 40% toc do 6s", 6, "slow_motion", 0.6, (100, 180, 255), "🦥", "rare"),
    Buff("Auto Perfect Ngan", "Tu dong Perfect 4s", 4, "auto_perfect", 1, (0, 255, 255), "🎯", "rare"),
    Buff("Combo Shield", "Giu combo khi miss 5s", 5, "combo_shield", 1, (255, 200, 255), "🔗", "rare"),
]

BUFF_LEGENDARY = [
    Buff("Hoi Mau Toan Bo", "Hoi 50% HP", 0, "hp_regen_percent", 50, (255, 50, 50), "❤️‍🔥", "legendary"),
    Buff("Tang Diem Cuc Manh", "Nhan 8 diem 10s", 10, "double_score", 8, (200, 100, 255), "💎", "legendary"),
    Buff("Dong Bang Thoi Gian", "Giam 80% toc do 5s", 5, "slow_motion", 0.2, (150, 220, 255), "❄️", "legendary"),
    Buff("Bat Tu Ngan", "Khong mat mau 8s", 8, "invincible", 1, (255, 200, 0), "👑", "legendary"),
    Buff("Auto Perfect Dai", "Tu dong Perfect 10s", 10, "auto_perfect", 1, (255, 100, 0), "🔥", "legendary"),
]

DEBUFF_COMMON = [
    Buff("Suong Mu Nhe", "Note doi thu mo 5s", 5, "opponent_fog", 0.3, (200, 200, 255), "👻", "common", True),
    Buff("Miss Gia Ngan", "Node doi thu luon MISS 3s", 3, "opponent_auto_miss", 1, (255, 150, 100), "💢", "common", True),
    Buff("Tang Toc Doi Thu", "Toc do note doi thu +30% 6s", 6, "opponent_speed_up", 1.3, (255, 200, 100), "⚡", "common", True),
]

DEBUFF_RARE = [
    Buff("Suong Mu Day", "Note doi thu rat mo 8s", 8, "opponent_fog", 0.6, (180, 180, 255), "🌫️", "rare", True),
    Buff("Miss Gia Dai", "Node doi thu luon MISS 5s", 5, "opponent_auto_miss", 1, (255, 100, 80), "🔥", "rare", True),
    Buff("Dao Lon", "Note doi thu dao nguoc 7s", 7, "opponent_invert", 1, (255, 100, 255), "🔄", "rare", True),
]

DEBUFF_LEGENDARY = [
    Buff("Mu Hoan Toan", "Note doi thu gan vo hinh 5s", 5, "opponent_fog", 0.9, (100, 100, 150), "🕶️", "legendary", True),
    Buff("Dong Bang Doi Thu", "Note doi thu dung yen 6s", 6, "opponent_freeze", 0.1, (100, 200, 255), "🧊", "legendary", True),
    Buff("Phan Sat Thuong", "Doi thu tu mat 5% mau moi hit", 8, "opponent_reflect", 5, (255, 50, 100), "🔮", "legendary", True),
]

def get_random_buff():
    roll = random.randint(1, 100)
    if roll <= 60:
        pool = BUFF_COMMON
    elif roll <= 90:
        pool = BUFF_RARE
    else:
        pool = BUFF_LEGENDARY
    return random.choice(pool)

def get_random_debuff():
    roll = random.randint(1, 100)
    if roll <= 60:
        pool = DEBUFF_COMMON
    elif roll <= 90:
        pool = DEBUFF_RARE
    else:
        pool = DEBUFF_LEGENDARY
    return random.choice(pool)

class ActiveBuff:
    def __init__(self, buff):
        self.buff = buff
        self.remaining_time = buff.duration
        self.active = True
        self.shield_used = False

    def update(self, dt):
        if self.buff.duration > 0:
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.active = False

    @property
    def duration(self):
        return self.buff.duration

    @property
    def effect_type(self):
        return self.buff.effect_type

    @property
    def effect_value(self):
        return self.buff.effect_value

    @property
    def is_debuff(self):
        return self.buff.is_debuff