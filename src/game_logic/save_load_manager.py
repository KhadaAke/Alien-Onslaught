"""
The save_load_manager module contains the SaveLoadSystem class that
implements the functionality of saving and loading the game.
"""

import pickle
import os
import time

import pygame

from src.entities.alien_entities.aliens import Alien, BossAlien
from src.utils.constants import DATA_KEYS, ATTRIBUTE_MAPPING


class SaveLoadSystem:
    """This class implements the Save/Load funcionality in the game."""

    def __init__(self, game, file_extension, save_folder):
        self.game = game
        self.file_extension = file_extension
        self.save_folder = save_folder
        self.data = {}

    def get_data(self, data_name, data):
        """Helper method that assigns data to the data dict."""
        self.data[data_name] = data

    def get_current_game_stats(self):
        """Retrieves and stores the current game statistics."""
        data_names = {
            "aliens": self.game.aliens,
            "level": self.game.stats.level,
            "high_score": self.game.stats.high_score,
            "thunderbird_score": self.game.stats.thunderbird_score,
            "phoenix_score": self.game.stats.phoenix_score,
            "thunderbird_hp": self.game.stats.thunderbird_hp,
            "phoenix_hp": self.game.stats.phoenix_hp,
            "thunderbird_ship_speed": self.game.settings.thunderbird_ship_speed,
            "thunderbird_bullet_speed": self.game.settings.thunderbird_bullet_speed,
            "thunderbird_bullets_allowed": self.game.settings.thunderbird_bullets_allowed,
            "thunderbird_bullet_count": self.game.settings.thunderbird_bullet_count,
            "thunderbird_remaining_bullets": self.game.thunderbird_ship.remaining_bullets,
            "thunderbird_missiles_num": self.game.thunderbird_ship.missiles_num,
            "phoenix_ship_speed": self.game.settings.phoenix_ship_speed,
            "phoenix_bullet_speed": self.game.settings.phoenix_bullet_speed,
            "phoenix_bullets_allowed": self.game.settings.phoenix_bullets_allowed,
            "phoenix_bullet_count": self.game.settings.phoenix_bullet_count,
            "phoenix_remaining_bullets": self.game.phoenix_ship.remaining_bullets,
            "phoenix_missiles_num": self.game.phoenix_ship.missiles_num,
            "alien_speed": self.game.settings.alien_speed,
            "alien_bullet_speed": self.game.settings.alien_bullet_speed,
            "alien_points": self.game.settings.alien_points,
            "fleet_rows": self.game.settings.fleet_rows,
            "last_bullet_rows": self.game.settings.last_bullet_rows,
            "aliens_num": self.game.settings.aliens_num,
            "alien_direction": self.game.settings.alien_direction,
            "alien_bullets_num": self.game.settings.alien_bullets_num,
            "max_alien_bullets": self.game.settings.max_alien_bullets,
            "boss_hp": self.game.settings.boss_hp,
            "boss_points": self.game.settings.boss_points,
            "asteroid_speed": self.game.settings.asteroid_speed,
            "asteroid_freq": self.game.settings.asteroid_freq,
            "speedup_scale": self.game.settings.speedup_scale,
            "thunder_ship_name": self.game.thunderbird_ship.ship_name,
            "phoenix_ship_name": self.game.phoenix_ship.ship_name,
            "game_mode": self.game.settings.game_modes.game_mode,
            "endless_onslaught": self.game.settings.game_modes.endless_onslaught,
            "slow_burn": self.game.settings.game_modes.slow_burn,
            "meteor_madness": self.game.settings.game_modes.meteor_madness,
            "boss_rush": self.game.settings.game_modes.boss_rush,
            "last_bullet": self.game.settings.game_modes.last_bullet,
            "cosmic_conflict": self.game.settings.game_modes.cosmic_conflict,
            "one_life_reign": self.game.settings.game_modes.one_life_reign,

        }

        for data_name, data_value in data_names.items():
            self.get_data(data_name, data_value)

    def check_alien_states(self):
        """Check the states of the aliens in the game and
        perform corresponding power actions.
        """
        if any(sprite.frozen_state for sprite in self.game.aliens):
            self.game.powers_manager.freeze_enemies()

        if any(sprite.immune_state for sprite in self.game.aliens):
            self.game.powers_manager.alien_upgrade()

    def save_data(self, name):
        """Saves the current game data to a file."""
        file_path = os.path.join(self.save_folder, f"{name}.{self.file_extension}")
        alien_sprites = self.data["aliens"]

        sprite_data = {
            "alien_sprites": [
                {"rect": sprite.rect,
                "size": sprite.image.get_size(),
                "image": pygame.image.tostring(sprite.image, "RGBA"),
                "is_baby": sprite.is_baby if not isinstance(sprite, BossAlien) else False, 
                "type": "boss" if isinstance(sprite, BossAlien) else "alien",
                "location": sprite.rect.x,
                "hit_count": sprite.hit_count,
                "last_bullet_time": sprite.last_bullet_time,
                "immune_state": sprite.immune_state if isinstance(sprite, Alien) else None,
                "frozen_state": sprite.frozen_state,
            }
                for sprite in alien_sprites
            ],
        }

        game_data = {
            "sprite_data": sprite_data,
            **{
                key: self.data[key]
                for key in DATA_KEYS
            },
        }

        with open(file_path, "wb") as file:
            pickle.dump(game_data, file)

    def load_data(self, name):
        """Loads game data from a file and updates the game state."""
        file_path = os.path.join(self.save_folder, f"{name}.{self.file_extension}")
        with open(file_path, "rb") as file:
            loaded_data = pickle.load(file)

        self.load_game_data(loaded_data)
        self.load_sprites(loaded_data)

    def load_sprites(self, loaded_data):
        """Loads and recreates the game sprites from the provided data."""
        sprite_data = loaded_data["sprite_data"]
        alien_sprites = self.game.aliens
        alien_sprites.empty()

        for sprite_state in sprite_data.get("alien_sprites", []):
            size = sprite_state["size"]

            sprite = self.create_alien_sprite(sprite_state["type"], sprite_state, self.game)

            sprite.size = size
            sprite.rect = sprite_state["rect"]
            sprite.image = pygame.image.fromstring(sprite_state["image"], size, "RGBA")
            sprite.x_pos = sprite_state["location"]
            sprite.frozen_state = sprite_state["frozen_state"]
            sprite.immune_state = sprite_state["immune_state"]
            sprite.last_bullet_time = sprite_state["last_bullet_time"]

            alien_sprites.add(sprite)

    def create_alien_sprite(self, sprite_type, sprite_state, game):
        """Create an alien sprite based on the given sprite type and state."""
        if sprite_type == "boss":
            sprite = BossAlien(game)
        elif sprite_type == "alien" and sprite_state["is_baby"]:
            sprite = Alien(game, baby_location=sprite_state["location"], is_baby=True)
            sprite.animation.change_scale(0.5)
        else:
            sprite = Alien(game)

        return sprite

    def load_game_data(self, loaded_data):
        """Loads the game data from a dictionary and applies it to the relevant game objects."""
        for key in DATA_KEYS:
            if key in ATTRIBUTE_MAPPING:
                attributes = ATTRIBUTE_MAPPING[key]
                obj = self.game
                for attribute in attributes[:-1]:
                    obj = getattr(obj, attribute)
                setattr(obj, attributes[-1], loaded_data[key])
            elif hasattr(self.game.stats, key) or hasattr(self.game.settings, key):
                setattr(
                    self.game.stats if hasattr(self.game.stats, key) else self.game.settings,
                    key,
                    loaded_data[key],
                )
