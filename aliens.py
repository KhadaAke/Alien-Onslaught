"""
Alien module
This module contains the class for creating instances of aliens and bosses.
"""
import math
import random
import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to represent an alien."""

    LEVEL_PREFIX = {
        0: "Alien1",
        1: "Alien2",
        2: "Alien3",
        3: "Alien4",
        4: "Alien4"
    }

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.last_bullet_time = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_delay = 70
        self.hit_count = 0
        self.direction = self.settings.alien_direction
        self.last_direction_change_time = pygame.time.get_ticks()
        self.direction_change_delay = 0

        alien_prefix = self.LEVEL_PREFIX.get(ai_game.stats.level // 2, "Alien4")
        self.frames = self.load_images(alien_prefix)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width   # Start each new alien near the top left of the screen.
        self.rect.y = self.rect.height

        self.time_offset = random.uniform(0, 2*math.pi)
        self.amplitude = random.randint(1, 2)
        self.frequency = random.uniform(0.001, 0.02)

        self.x_pos = float(self.rect.x)


    @staticmethod
    def load_images(alien_prefix):
        """Load the images for the given alien prefix."""
        frames = []
        for i in range(6):
            filename = f'images/aliens/{alien_prefix}_{i}.png'
            frame = pygame.image.load(filename)
            frames.append(frame)

        return frames

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if (self.rect.right >= screen_rect.right or self.rect.left <= 0 or
            self.rect.top <= 0):
            return True


    def update(self):
        """Update alien position on screen."""
        # Update current frame
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.last_update_time = now

        self.x_pos += self.settings.alien_speed * self.direction
        self.rect.x = round(self.x_pos)

        # Change horizontal direction
        now = pygame.time.get_ticks()
        if now - self.last_direction_change_time > self.direction_change_delay:
            # Check if alien is not near the edge of the screen
            if not self.check_edges():
                self.direction *= -1
            self.last_direction_change_time = now
            # how often the direction changes
            self.direction_change_delay = random.randint(3000, 5000) # miliseconds

        # Change vertical direction
        now = pygame.time.get_ticks()
        time = now + self.time_offset
        self.rect.y = round(self.rect.y + self.amplitude * math.sin(self.frequency * time))


class BossAlien(Sprite):
    """A class to represent Boss Aliens"""
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/aliens/first_boss.png')
        self.second_boss = pygame.image.load('images/aliens/second_boss.png')
        self.mothership = pygame.image.load('images/aliens/mothership.png')
        self.check_level(ai_game)

        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-30, 0)
        self.last_bullet_time = 0
        self.hit_count = 1
        self.direction = self.settings.alien_direction
        self.last_direction_change_time = pygame.time.get_ticks()
        self.direction_change_delay = 0

        self.rect.x =  self.rect.width
        self.rect.y = self.rect.height - self.image.get_height() + 50
        self.x_pos = float(self.rect.x)


    def check_level(self, ai_game):
        """Change image for specific boss fight"""
        if ai_game.stats.level == 14:
            self.image = self.second_boss
        elif ai_game.stats.level == 19:
            self.image = self.mothership

    def update(self):
        """Move the boss alien down the screen."""
        self.x_pos += self.settings.alien_speed * self.direction
        self.rect.x = round(self.x_pos)

        # Change direction
        now = pygame.time.get_ticks()
        if now - self.last_direction_change_time > self.direction_change_delay:
            # Check if alien is not near the edge of the screen
            if not self.check_edges():
                self.direction *= -1
            self.last_direction_change_time = now
            self.direction_change_delay = random.randint(3000, 5000)

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
