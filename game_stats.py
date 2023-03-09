"""
Game stats module
This module contains code that manages the statistics that change during the game.
"""

class GameStats:
    """Track statistics for the game."""
    def __init__(self, ai_game, phoenix_ship, thunderbird_ship):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats(phoenix_ship, thunderbird_ship)
        self.game_active = False
        self.high_score = 0

    def reset_stats(self, phoenix_ship, thunderbird_ship):
        """Initialize statistics that can change during the game."""
        phoenix_ship.alive = True
        thunderbird_ship.alive = True
        self.phoenix_hp = self.settings.phoenix_hp
        self.thunderbird_hp = self.settings.thunderbird_hp
        self.max_hp = self.settings.max_hp
        self.thunder_bullets = self.settings.thunderbird_bullet_count
        self.fire_bullets = self.settings.phoenix_bullet_count
        self.score = 0
        self.second_score = 0
        self.level = 1
        self.bg_img = self.settings.bg_img
