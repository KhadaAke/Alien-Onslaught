"""
Health module
This module contains the class that creates the health for the players
"""

import pygame
from pygame.sprite import Sprite


class Heart(Sprite):
    """A class that manages the remaining health of player/players"""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        self.image = pygame.image.load('images/power_ups/heart.png')
        self.rect = self.image.get_rect(topleft = (0, 0))

    def blitme(self):
        """Draws the image"""
        self.screen.blit(self.image, self.rect)
