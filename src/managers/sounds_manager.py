"""
The 'sounds_manager' module contains the `SoundManager` class which manages
different sounds in the game. Additionally, it handles the loading of sound
files for usage throughout the game.
"""

import pygame

from src.utils.constants import (
    LEVEL_SOUNDS,
    MENU_SOUNDS,
    MENU_MUSIC,
    GAME_SOUNDS,
    BOSS_RUSH_MUSIC,
    ENDLESS_SOUNDTRACK,
    METEOR_MADNESS_MUSIC,
)
from src.utils.game_utils import (
    load_sound_files,
    set_sounds_volume,
    set_music_volume,
    load_music_files,
    play_music,
    display_muted_state_message,
    play_sound,
)


class SoundManager:
    """This class is responsible for loading and playing various
    sound effects and music.
    """

    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.loading_screen = game.loading_screen
        self.stats = game.stats

        (
            self.menu_music,
            self.level_music,
            self.menu_sounds,
            self.game_sounds,
            self.boss_rush_levels,
            self.endless_music,
            self.meteor_music,
        ) = ({}, {}, {}, {}, {}, {}, {})

        self.current_sound = None
        self.draw_muted_message = False
        self.display_muted_time = 0

    def load_sounds(self, sounds_to_load):
        """Load necessary sound files."""
        if sounds_to_load == "gameplay_sounds":
            self._load_gameplay_sounds()
            self._set_multiple_music_volume(0.3)
            self._prepare_gameplay_sounds_volume()
        elif sounds_to_load == "menu_sounds":
            self.load_menu_sounds()
            set_music_volume(self.menu_music, 0.8)
            set_sounds_volume(self.menu_sounds, 0.7)

    def _load_gameplay_sounds(self):
        """Load the sound files for the level-specific music and game sounds
        while displaying the loading screen.
        """
        while not (self.level_music and self.game_sounds):
            self.loading_screen.update(25)
            self.level_music = load_music_files(LEVEL_SOUNDS)
            self.boss_rush_levels = load_music_files(BOSS_RUSH_MUSIC)
            self.endless_music = load_music_files(ENDLESS_SOUNDTRACK)
            self.meteor_music = load_music_files(METEOR_MADNESS_MUSIC)
            self.loading_screen.update(75)
            self.game_sounds = load_sound_files(GAME_SOUNDS)
            self.loading_screen.update(100)

    def load_menu_sounds(self):
        """Load the sound files for the menu while displaying the loading screen."""
        while not (self.menu_sounds and self.menu_music):
            self.loading_screen.update(25)
            self.menu_sounds = load_sound_files(MENU_SOUNDS)
            self.menu_music = load_music_files(MENU_MUSIC)
            self.loading_screen.update(100)

    def _set_level_music(self):
        """Determine the appropriate music dictionary
        based on the current game mode."""
        if self.settings.game_modes.boss_rush:
            return self.boss_rush_levels

        if self.settings.game_modes.endless_onslaught:
            return self.endless_music

        if self.settings.game_modes.meteor_madness:
            return self.meteor_music

        return self.level_music

    def prepare_level_music(self):
        """This method determines the appropriate background music
        to play based on the current game mode and level.
        """
        music_to_play = self._set_level_music()

        for key, sound_name in music_to_play.items():
            if self.stats.level in key:
                if sound_name != self.current_sound:
                    play_music(music_to_play, key)
                    self.current_sound = sound_name
                return

    def _prepare_gameplay_sounds_volume(self):
        """Prepare the volume for specific sounds."""
        self.game_sounds["bullet"].set_volume(0.1)
        self.game_sounds["alien_exploding"].set_volume(0.5)

    def _get_music_dicts(self):
        """Retrieve the dictionaries containing the loaded music files."""
        return {
            "level_music": self.level_music,
            "boss_rush_levels": self.boss_rush_levels,
            "endless_music": self.endless_music,
            "meteor_music": self.meteor_music,
        }

    def _set_multiple_music_volume(self, volume):
        """Set the volume of multiple game music items."""
        music_dicts = self._get_music_dicts()
        for music_dict in music_dicts.values():
            for _ in music_dict.values():
                pygame.mixer.music.set_volume(volume)

    def check_music_volume(self):
        """Check if the music should be muted or not."""
        if self.game.music_muted:
            pygame.mixer.music.set_volume(0)

    def check_sfx_volume(self):
        """Check if sfx should be muted or not."""
        if self.game.sfx_muted:
            all_sfx = {**self.game_sounds, **self.menu_sounds}

            for sound in all_sfx.values():
                sound.set_volume(0.0)

    def toggle_mute_music(self, scope):
        """Toggle the music mute state."""
        self.game.music_muted = not self.game.music_muted
        self.draw_muted_message = True

        if self.game.music_muted:
            play_sound(self.menu_sounds, "is_muted")
        elif not self.game.music_muted:
            play_sound(self.menu_sounds, "is_unmuted")

        volume_mapping = {"game": 0.3, "menu": 0.8}

        volume = 0 if self.game.music_muted else volume_mapping.get(scope, 1)

        pygame.mixer.music.set_volume(volume)

    def toggle_mute_sfx(self):
        """Toggle the sfx mute state."""
        self.game.sfx_muted = not self.game.sfx_muted
        self.draw_muted_message = True

        if self.game.sfx_muted:
            play_sound(self.menu_sounds, "is_muted")
        elif not self.game.sfx_muted:
            play_sound(self.menu_sounds, "is_unmuted")

        volume = 0 if self.game.sfx_muted else 1
        menu_sounds_volume = 0 if self.game.sfx_muted else 0.7
        alien_ex_volume = 0.5 if not self.game.sfx_muted else 0
        bullet_volume = 0.1 if not self.game.sfx_muted else 0

        for name, sound in self.game_sounds.items():
            if name == "bullet":
                sound.set_volume(bullet_volume)
            elif name == "alien_exploding":
                sound.set_volume(alien_ex_volume)
            else:
                sound.set_volume(volume)

        for name, sound in self.menu_sounds.items():
            if name == "is_muted" or name == "is_unmuted":
                sound.set_volume(0.8)
            else:
                sound.set_volume(menu_sounds_volume)

    def check_muted_state(self):
        """Check the muted state of music and sound effects and display a message if needed."""
        current_time = pygame.time.get_ticks()

        if self.draw_muted_message:
            if current_time - self.display_muted_time <= 1500:
                music_message = ""
                sfx_message = ""
                if self.game.music_muted:
                    music_message = "Music Muted"
                elif not self.game.music_muted:
                    music_message = "Music Unmuted"

                if self.game.sfx_muted:
                    sfx_message = "SFX Muted"
                elif not self.game.sfx_muted:
                    sfx_message = "SFX Unmuted"

                message = music_message + " | " + sfx_message
                display_muted_state_message(self.game.screen, message)
            else:
                self.draw_muted_message = False

        if not self.draw_muted_message:
            self.display_muted_time = current_time
