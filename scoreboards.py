"""
Scoreboard module
This module contains the class that reports the scoring information such as:
highscore, players score, health, level.
"""
import json
import pygame.font
from pygame.sprite import Group
from player_health import Heart

class ScoreBoard:
    """A class to report scoring information."""
    def __init__(self, ai_game):
        """Initialize scorekeeping attributes."""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.second_stats = ai_game.stats

        # Font settings
        self.text_color = 'red'
        self.level_color = 'blue'
        self.font = pygame.font.SysFont('', 27)

        # Prepare the initial score images.
        self.prep_level()
        self.prep_score()
        self.prep_high_score()
        self.prep_hp()

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score)
        rounded_second_score = round(self.second_stats.second_score)
        score_str = f"Thunderbird: {rounded_score:,}"
        second_score_str = f"Phoenix: {rounded_second_score:,}"
        self.score_image = self.font.render(score_str, True,
            self.text_color, None)
        self.second_score_image = self.font.render(second_score_str, True,
            self.text_color, None)

        # Display the scores at the stop right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.level_rect.centerx - 200
        self.score_rect.top = 20

        self.second_score_rect = self.second_score_image.get_rect()
        self.second_score_rect.right = self.level_rect.centerx + 300
        self.second_score_rect.top = 20


    def prep_high_score(self):
        """Turn the high score intro a rendered image."""
        high_score = round(self.stats.high_score)
        high_score_str = f"High Score: {high_score:,}"
        self.high_score_image = self.font.render(high_score_str, True,
            self.text_color, None)

        # Center the high score at the top of the screen.
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.level_rect.centerx
        self.high_score_rect.top = self.score_rect.top


    def check_high_score(self):
        """Check if there's a new high score."""
        if self.stats.score + self.second_stats.second_score > self.stats.high_score:
            self.stats.high_score = self.stats.score + self.second_stats.second_score
            self.prep_high_score()

    def prep_level(self):
        """Turn the level into a rendered image."""
        if self.settings.endless:
            level_str =  "Endless Onslaught"
        elif self.settings.last_stand:
            level_str = "Last Stand level " + str(self.stats.level)
        else:
            level_str = "Level " + str(self.stats.level)
        self.level_image = self.font.render(level_str, True, self.level_color, None)

        # Position the level image in the center of the screen.
        screen_width, _ = self.screen.get_size()
        _, level_height = self.level_image.get_size()
        self.level_rect = self.level_image.get_rect()
        self.level_rect.centerx = screen_width // 2
        self.level_rect.top = 25 + level_height


    def prep_hp(self):
        """Creates the health sprites for both players."""
        self.hearts = Group()
        for heart_number in range(self.stats.thunderbird_hp):
            heart = Heart(self.ai_game)
            heart.rect.x = 10 + heart_number * heart.rect.width
            heart.rect.y = 10
            self.hearts.add(heart)

        self.second_hearts = Group()
        for second_heart_num in range(self.stats.phoenix_hp):
            second_heart = Heart(self.ai_game)
            second_heart.rect.x = (
                self.settings.screen_width -
                (10 + (second_heart_num + 1) * second_heart.rect.width))
            second_heart.rect.y = 10
            self.second_hearts.add(second_heart)


    def save_high_score(self):
        """Save the high score to a JSON file."""
        filename = 'high_score.json'
        try:
            with open(filename, 'r', encoding='utf-8') as score_file:
                high_scores = json.load(score_file)
        except json.JSONDecodeError:
            high_scores = {'high_scores': [0] * 10}

        scores = high_scores['high_scores']
        new_score = self.stats.score + self.second_stats.second_score

        if new_score not in scores:
            scores.append(new_score)
            scores.sort(reverse=True)
            scores = scores[:10]
            high_scores['high_scores'] = scores

            with open(filename, 'w', encoding='utf-8') as score_file:
                json.dump(high_scores, score_file)


    def show_score(self):
        """Draw scores, level and health to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.second_score_image, self.second_score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.hearts.draw(self.screen)
        self.second_hearts.draw(self.screen)


class SecondScoreBoard(ScoreBoard):
    """A class to report scoring information for the single player mode."""

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score)
        score_str = f"Score: {rounded_score:,}"
        self.score_image = self.font.render(score_str, True,
            self.text_color, None)

        # Display the score at the stop right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.level_rect.centerx + 250
        self.score_rect.top = 20

    def prep_high_score(self):
        """Turn the high score intro a rendered image."""
        high_score = round(self.stats.high_score)
        high_score_str = f"High Score: {high_score:,}"
        self.high_score_image = self.font.render(high_score_str, True,
            self.text_color, None)

        # Center the high score at the top of the screen.
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.level_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def check_high_score(self):
        """Check to see if there's a new high score."""
        if self.stats.score  > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        """Draw scores, level and health to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.hearts.draw(self.screen)
