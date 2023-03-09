"""
Asteroid module
This module contains the class for creating instances of asteroids in the game.
"""

import random
import pygame
from pygame.sprite import Sprite


class Asteroid(Sprite):
    """A class that manages the power ups for the game"""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load asteroid frames and set initial frame
        self.frames = []
        for i in range(120):
            filename = f'images/asteroid/Asteroid-A-09-{i:03d}.png'
            frame = pygame.image.load(filename)
            self.frames.append(frame)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        # Set initial position and speed
        self.rect = self.frames[0].get_rect()
        self.rect.x = random.randint(0, self.settings.screen_width - self.rect.width)
        self.rect.y = 0
        self.y_pos = float(self.rect.y)
        self.speed = self.settings.powerup_speed

    def update(self):
        # Update current frame
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]

        # Update position
        self.y_pos += self.speed
        self.rect.y = self.y_pos

    def draw_asteroid(self):
        """Draws the asteroid"""
        self.screen.blit(self.image, self.rect)
