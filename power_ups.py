"""
Power-ups module
This module contains the class for creating instances of power-ups.
"""

import random
import pygame
from pygame.sprite import Sprite



class PowerUp(Sprite):
    """A class that manages the power ups for the game"""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/power_ups/power_up.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, self.settings.screen_width - self.rect.width)
        self.rect.y = 0

        self.y_pos = float(self.rect.y)
        self.speed = self.settings.powerup_speed

    def update(self):
        """Updates the power ups"""
        self.y_pos += self.speed
        self.rect.y = self.y_pos


    def draw_powerup(self):
        """Draws the power ups on the screen"""
        self.screen.blit(self.image, self.rect)


class HealthPowerUp(Sprite):
    """A class that manages the health power-ups for the game"""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/power_ups/health.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, self.settings.screen_width - self.rect.width)
        self.rect.y = 0

        self.y_pos = float(self.rect.y)
        self.speed = self.settings.powerup_speed

    def update(self):
        """Updates power up"""
        self.y_pos += self.speed
        self.rect.y = self.y_pos

    def draw_powerup(self):
        """Drawas the power up on the screen"""
        self.screen.blit(self.image, self.rect)
