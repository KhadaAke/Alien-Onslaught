"""
Bullets module
This module contains the classes for the ship bullets
"""

import pygame
from pygame.sprite import Sprite



class Thunderbolt(Sprite):
    """A class to manage bullets for the Player 1 ship"""
    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/player_bullets/blue.png')
        self.rect = self.image.get_rect()
        self.rect.midtop = (ai_game.thunderbird_ship.rect.centerx,
                             ai_game.thunderbird_ship.rect.top)


        self.y_pos = float(self.rect.y)   # Store the bullet's position as a decimal value.

    def update(self):
        """Move the bullet up the screen."""
        self.y_pos -= self.settings.thunderbird_bullet_speed   
        self.rect.y = self.y_pos 

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect)


class Firebird(Thunderbolt):
    """A class to manage bullets for the Player 2 ship."""
    def __init__(self, ai_game):
        super().__init__(ai_game)
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/player_bullets/red.png')
        self.rect = self.image.get_rect()
        self.rect.midtop = (ai_game.phoenix_ship.rect.centerx,
                             ai_game.phoenix_ship.rect.top)
        self.y_pos = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen"""
        self.y_pos -= self.settings.phoenix_bullet_speed
        self.rect.y = self.y_pos
