"""
Game stats module
This module contains code that manages the statistics that change during the game.
"""

class GameStats:
    """Track statistics for the game."""
    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = 0

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.player_one_active = True
        self.player_two_active = True
        self.player_two_hp = self.settings.player_two_hp
        self.ships_left = self.settings.ship_limit
        self.max_ships = self.settings.max_ships
        self.thunder_bullets = self.settings.thunder_bullet_count
        self.fire_bullets = self.settings.fire_bullet_count
        self.score = 0
        self.second_score = 0
        self.level = 1
        self.bg_img = self.settings.bg_img
