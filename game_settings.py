"""
Settings module
This module contains the settings for the game such as:
background , sounds, bullet, ships, aliens, game difficulty.
"""
import pygame


class Settings:
    """A class to store all settings for Alien Invasion."""
    def __init__(self):
        """Initialize the game's static settings."""
        # Screen Settings
        self.screen_size = (1250, 660)
        self.screen_width = 1250
        self.screen_height = 660
        # game background images
        self.bg_img = pygame.image.load('images/background/space.jpg')
        self.second_bg = pygame.image.load('images/background/space2.png')
        self.third_bg = pygame.image.load('images/background/space4.jpg')
        self.game_over = pygame.image.load('images/other/gameover.png')
        self.pause = pygame.image.load('images/other/pause.png')
        self.fire_sound = pygame.mixer.Sound('sounds/fire.wav')

        # Ships settings
        self.max_hp = 5
        self.thunderbird_hp = 3
        self.phoenix_hp = 3

        # Thunderbolt settings
        self.thunderbird_bullet_count = 1

        # Firebird settings
        self.phoenix_bullet_count = 1

        # Alien settings
        self.alien_direction = 1
        self.max_alien_speed = 4.0
        self.boss_hp = 50
        self.boss_points = 2500
        self.alien_points = 1

        # PowerUps settings
        self.powerup_speed = 1.5

        # How quickly the game speeds up
        self.speedup_scale = 0.3

        self.score_scale = 4
        self.initialize_dynamic_settings()

        # Player1 controls
        self.p1_controls = ("Player 1:\n"
                            "Movement: Arrow Keys\n"
                            "Shoot: Enter\n"
                            "Ship skin: Numpad 1, 2, 3\n"
                            "Pause: P")

        # Player2 controls
        self.p2_controls = ("Player 2:\n"
                            "Movement: W, A, S, D\n"
                            "Shoot: Space\n"
                            "Ship skin: 1, 2, 3\n"
                            "Pause: P")

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game"""
        self.thunderbird_ship_speed = 3.5
        self.phoenix_ship_speed = 3.5
        self.thunderbird_bullet_speed = 5.0
        self.phoenix_bullet_speed = 5.0
        self.alien_speed = 1.2
        self.alien_bullet_speed = 1.5
        self.thunderbird_bullets_allowed = 1
        self.phoenix_bullets_allowed = 1

        # Scoring
        self.alien_points = 1

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        if self.alien_speed < self.max_alien_speed:
            self.alien_speed += self.speedup_scale
            self.alien_bullet_speed += self.speedup_scale
        self.alien_points = int(self.alien_points + self.score_scale)
        # bosses have more hp on medium or hard difficulty
        if self.speedup_scale == 0.5:
            self.boss_hp = 75
        elif self.speedup_scale == 0.7:
            self.boss_hp = 100
