"""
Ships module
This module contains the class definitons for the ships in the game
Here are also both shield and explosion animation for each ship.
"""

import pygame
from pygame.sprite import Sprite


class Thunderbird(Sprite):
    """A class to manage the Player 1 ship."""

    def __init__(self, ai_game, x, y):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        self.image = pygame.image.load('images/ships/ship1.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.bullet_power = True
        self.exploding = False
        self.shield_on = False
        self.is_warping = False
        self.single_player = False

        # Movement flags
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        self.ship_images = []
        self.load_ship_images()

        # Explosion animation
        self.explosion_frames = []
        self.load_explosion_frames()

        self.current_frame = 0
        self.explosion_image = self.explosion_frames[self.current_frame]
        self.explosion_rect = self.explosion_image.get_rect()

        # Shield animation
        self.shield_frames = []
        self.load_shield_frames()

        self.current_shield_frame = 0
        self.shield_image = self.shield_frames[self.current_shield_frame]
        self.shield_rect = self.shield_image.get_rect()

        # Warp animation
        self.warp_images = []
        self.warp_index = 0
        self.warp_delay = 5
        self.warp_counter = 0
        self.load_warp_images()

        # Movement variables
        self.x_pos = float(self.rect.x)
        self.y_pos = float(self.rect.y)


    def load_ship_images(self):
        """Loads a series ship images"""
        for i in range(1, 7):
            filename = f'images/ships/ship{i}.png'
            frame = pygame.image.load(filename)
            self.ship_images.append(frame)

    def load_explosion_frames(self):
        """Loads a series of explosion animation frames"""
        for i in range(2, 89):
            filename = f'images/explosionn/explosion1_{i:04d}.png'
            frame = pygame.image.load(filename)
            self.explosion_frames.append(frame)

    def load_shield_frames(self):
        """Loads a series of shield animation frames"""
        for i in range(11):
            filename = f'images/shield/shield-0{i}.png'
            frame = pygame.image.load(filename)
            self.shield_frames.append(frame)

    def load_warp_images(self):
        """Loads a series of warp animation frames"""
        for i in range(9):
            filename = f'images/warp/warp_{i}.png'
            frame = pygame.image.load(filename)
            self.warp_images.append(frame)

    def update_state(self):
        """Update the ship's position based on the movement flags."""
        if not self.exploding:
            if self.is_warping:
                self.warp_counter += 1
                if self.warp_counter >= self.warp_delay:
                    self.warp_index += 1
                    if self.warp_index >= len(self.warp_images):
                        self.is_warping = False
                        self.warp_index = 0
                        self.image = self.ship_images[0]  # Reset to regular ship image
                    else:
                        self.image = self.warp_images[self.warp_index]
                    self.warp_counter = 0

            # Update the ship's x value, not the rect.
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.x_pos += self.settings.first_player_ship_speed
            if self.moving_left and self.rect.left > 0:
                self.x_pos -= self.settings.first_player_ship_speed
            if self.moving_up and self.rect.top > 0:
                self.y_pos -= self.settings.first_player_ship_speed
            if self.moving_down and self.rect.bottom <= self.screen_rect.bottom:
                self.y_pos += self.settings.first_player_ship_speed
        else:
            # Update the explosion animation
            self.current_frame = (self.current_frame + 1) % len(self.explosion_frames)
            self.explosion_image = self.explosion_frames[self.current_frame]
            if self.current_frame == 0:
                # If the animation is complete, reset the ship
                self.exploding = False
                self.center_ship()

        if self.shield_on:
            self.current_shield_frame = (self.current_shield_frame + 1) % len(self.shield_frames)
            self.shield_image = self.shield_frames[self.current_shield_frame]

        self.shield_rect.center = self.rect.center

        if self.single_player:
        # Update rect object from self.x_pos and self.y_pos for single player mode
            self.rect.x = int(self.x_pos)
            self.rect.y = int(self.y_pos - 10)
        else:
            # Update rect object from self.x_pos for multiplayer mode
            self.rect.x = int(self.x_pos - 250)
            self.rect.y = int(self.y_pos - 10)

    def blitme(self):
        """Draw the ship at its current location."""
        if self.is_warping:
            self.screen.blit(self.warp_images[self.warp_index], self.rect)
        elif not self.exploding:
            self.screen.blit(self.image, self.rect)
            if self.shield_on:
                self.screen.blit(self.shield_image, self.shield_rect)
        else:
            self.screen.blit(self.explosion_image, self.explosion_rect)

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x_pos = float(self.rect.x)
        self.y_pos = float(self.rect.y)

    def draw_shield(self):
        """Turns the shield on"""
        self.shield_on = True
        self.shield_rect.center = self.rect.center

    def explode(self):
        """Starts the explosion animation"""
        self.exploding = True
        self.explosion_rect.center = self.rect.center

    def start_warp(self):
        """Starts the warp animation"""
        self.is_warping = True


class Phoenix(Thunderbird):
    """A class to manage the Player 2 ship."""
    def __init__(self, ai_game, x, y):
        super().__init__(ai_game, x, y)
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/ships/ship4.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update_state(self):
        """Update the ship's state"""
        if not self.exploding:
            if self.is_warping:
                self.warp_counter += 1
                if self.warp_counter >= self.warp_delay:
                    self.warp_index += 1
                    if self.warp_index >= len(self.warp_images):
                        self.is_warping = False
                        self.warp_index = 0
                        self.image = self.ship_images[3]  # Reset to regular ship image
                    else:
                        self.image = self.warp_images[self.warp_index]
                    self.warp_counter = 0

            # Update the ship's x value, not the rect.
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.x_pos += self.settings.first_player_ship_speed
            if self.moving_left and self.rect.left > 0:
                self.x_pos -= self.settings.first_player_ship_speed
            if self.moving_up and self.rect.top > 0:
                self.y_pos -= self.settings.first_player_ship_speed
            if self.moving_down and self.rect.bottom <= self.screen_rect.bottom:
                self.y_pos += self.settings.first_player_ship_speed
        else:
            # Update the explosion animation
            self.current_frame = (self.current_frame + 1) % len(self.explosion_frames)
            self.explosion_image = self.explosion_frames[self.current_frame]
            if self.current_frame == 0:
                # If the animation is complete, reset the ship
                self.exploding = False
                self.center_ship()

        if self.shield_on:
            self.current_shield_frame = (self.current_shield_frame + 1) % len(self.shield_frames)
            self.shield_image = self.shield_frames[self.current_shield_frame]

        self.shield_rect.center = self.rect.center

        # Update rect object from self.x_pos.
        self.rect.x = int(self.x_pos + 250)
        self.rect.y = int(self.y_pos - 10)
