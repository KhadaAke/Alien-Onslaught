"""
Bullets module
This module contains the classes for alien bullets
"""

import random
import pygame
from pygame.sprite import Sprite


class AlienBullet(Sprite):
    """A class to manage bullets for the aliens."""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/alien_bullets/alien_bullet.png')
        self.rect = self.image.get_rect()

        random_alien = random.choice(ai_game.aliens.sprites())
        self.rect.centerx = random_alien.rect.centerx
        self.rect.bottom = random_alien.rect.bottom
        self.y_pos = float(self.rect.y)


    def update(self):
        self.y_pos += self.settings.alien_bullet_speed
        self.rect.y = self.y_pos

    def draw_bullet(self):
        """Draws the bullet"""
        self.screen.blit(self.image, self.rect)


class BossBullet(Sprite):
    """A class to manage bullets for the boss alien."""
    def __init__(self, ai_game, alien):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/alien_bullets/boss_bullet.png')
        self.second_bullet = pygame.image.load('images/alien_bullets/second_bullet.png')
        self.motherbullet = pygame.image.load('images/alien_bullets/mother_bullet.png')
        self.check_level(ai_game)
        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-50, -50)

        self.rect.centerx = alien.rect.centerx
        self.rect.centery = alien.rect.centery
        self.y_pos = float(self.rect.y)
        self.x_vel = random.uniform(-4, 4)

    def check_level(self, ai_game):
        """Change the bullet image for the specific boss fight"""
        if ai_game.stats.level == 15:
            self.image = self.second_bullet
        elif ai_game.stats.level == 20:
            self.image = self.motherbullet

    def update(self):
        """Move the bullet up the screen."""
        self.y_pos += self.settings.alien_bullet_speed
        self.rect.y = self.y_pos
        self.rect.x += round(self.x_vel)

    def draw_bullet(self):
        """Draws the bullet"""
        self.screen.blit(self.image, self.rect)
