"""The projectiles module contains different projectiles for the players"""

import pygame
from pygame.sprite import Sprite
from utils.frames import missile_frames
from utils.constants import SHIPS
from animations.other_animations import MissileEx



class Thunderbolt(Sprite):
    """A class to manage bullets for Thunderbird ship."""
    def __init__(self, game):
        """Create a bullet object at the ship's current position"""
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.image.load(SHIPS['thunderbolt'])
        self.rect = self.image.get_rect()
        self.rect.midtop = (game.thunderbird_ship.rect.centerx,
                            game.thunderbird_ship.rect.top)

        self.y_pos = float(self.rect.y)

    def update(self):
        """Update the bullet position on screen."""
        self.y_pos -= self.settings.thunderbird_bullet_speed
        self.rect.y = self.y_pos

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect)


class Firebird(Thunderbolt):
    """A class to manage bullets for Phoenix ship."""
    def __init__(self, game):
        super().__init__(game)
        self.image = pygame.image.load(SHIPS['firebird'])
        self.rect = self.image.get_rect()
        self.rect.midtop = (game.phoenix_ship.rect.centerx,
                             game.phoenix_ship.rect.top)

        self.y_pos = float(self.rect.y)

    def update(self):
        """Update the bullet position on screen."""
        self.y_pos -= self.settings.phoenix_bullet_speed
        self.rect.y = self.y_pos



class Missile(Sprite):
    """The Missile class represents a missile object in the game."""
    def __init__(self, game, ship):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.game = game
        self.ship = ship
        self.destroy_delay = 50

        self.frames = missile_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.frames[0].get_rect()
        self.rect.midtop = (self.ship.rect.centerx, self.ship.rect.top)

        self.y_pos = float(self.rect.y)

        self.frame_update_rate = 5  # Update the frame once every 3 game loops
        self.frame_counter = 0

        self.destroy_anim = MissileEx(self)
        self.is_destroyed = False

    def update(self):
        """Update the missile's position and animation."""
        if self.is_destroyed:
            if self.destroy_delay > 0:
                self.destroy_anim.update_animation()
                self.destroy_delay -= 1
            else:
                self.kill()
        else:
            self.frame_counter += 1
            if self.frame_counter % self.frame_update_rate == 0:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                self.frame_counter = 0

            self.y_pos -= self.settings.missiles_speed
            self.rect.y = self.y_pos

    def draw_missile(self):
        """Draw the missile or explosion effect,
        depending on whether it's destroyed or not."""
        if self.is_destroyed:
            self.destroy_anim.draw_explosion()
        else:
            self.screen.blit(self.image, self.rect)

    def explode(self):
        """Trigger the explosion effect."""
        self.is_destroyed = True