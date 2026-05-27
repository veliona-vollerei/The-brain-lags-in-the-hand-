import os
import random
import cv2
import pygame
import numpy as np
import math

def load_random_background(folder, screen_size):
    if not os.path.isdir(folder):
        return None
    allowed_ext = ('.jpg', '.jpeg', '.png', '.bmp')
    files = [f for f in os.listdir(folder) if f.lower().endswith(allowed_ext)]
    if not files:
        return None
    chosen = random.choice(files)
    path = os.path.join(folder, chosen)
    try:
        img = pygame.image.load(path).convert()
        img = pygame.transform.scale(img, screen_size)
        return img
    except:
        return None

def cv2_to_pygame(frame_bgr, target_size=None):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    if target_size:
        frame_rgb = cv2.resize(frame_rgb, target_size)
    surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    return surface

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=15, gap_length=10, width=2):
    x1, y1 = start_pos
    x2, y2 = end_pos
    if x1 == x2 and y1 == y2:
        return
    total_len = math.hypot(x2 - x1, y2 - y1)
    dx = (x2 - x1) / total_len
    dy = (y2 - y1) / total_len
    pos = 0
    drawing = True
    while pos < total_len:
        start_x = x1 + dx * pos
        start_y = y1 + dy * pos
        if drawing:
            end_len = min(dash_length, total_len - pos)
            end_x = start_x + dx * end_len
            end_y = start_y + dy * end_len
            pygame.draw.line(surface, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), width)
            pos += dash_length
        else:
            pos += gap_length
        drawing = not drawing