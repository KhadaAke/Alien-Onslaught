"""
The Alien Onslaught game module contains the multiplayer and singleplayer versions of the game.
This module imports all other classes and modules required to run the game.
In this game the players have to shoot fleets of aliens in order to
reach higher levels and increase their high score.


Author: [Miron Alexandru]
Date: 
"""
import json
import sys
import random
import time
import pygame

from game_settings import Settings
from game_stats import GameStats
from scoreboards import ScoreBoard, SecondScoreBoard
from button import Button
from ships import Thunderbird, Phoenix
from player_bullets import Thunderbolt, Firebird
from alien_bullets import AlienBullet, BossBullet
from aliens import Alien, BossAlien
from power_ups import PowerUp, HealthPowerUp
from asteroid import Asteroid


class AlienOnslaught:
    """Overall class to manage game assets and behavoir for the multiplayer version."""
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(self.settings.screen_size, pygame.RESIZABLE)
        self.bg_img = pygame.transform.smoothscale(self.settings.bg_img, self.screen.get_size())
        self.bg_img_rect = self.bg_img.get_rect()
        self.reset_bg = self.bg_img.copy()
        self.last_power_up_time, self.last_alien_bullet_time, self.last_asteroid_time = 0, 0, 0
        self.button_names = ["play_button", "quit_button", "menu_button",
                            'difficulty', 'easy', 'medium', 'hard', 'high_scores',
                            'game_modes', 'endless']
        self.button_images = self._load_button_images(self.button_names)
        self.paused, self.show_difficulty, self.resizable, \
        self.high_score_saved, self.show_high_scores, self.show_game_modes = \
        False, False, True, False, False, False
        self.last_increase_time = 0

        self._initialize_game_objects()
        self._initialize_game_buttons()
        self._initialize_game_over()
        self._initialize_start_menu()
        self._initialize_menu_buttons()

        pygame.display.set_caption("Alien Onslaught")


    def _initialize_start_menu(self):
        """Initializes variables for the start menu"""
        self.button_names = ["single_player", "multiplayer",
                            "player_controls", "menu_quit_button"]
        self.button_images = self._load_button_images(self.button_names)

        self.p1_controls, self.p1_controls_rect = self._load_controls_image(
                                                'player_controls',
                                                {'topleft': (50, 50)})
        self.p2_controls, self.p2_controls_rect = self._load_controls_image(
                                                'player_controls',
                                                {'topright':
                                                (self.settings.screen_width - 50, 50)})

        self.font = pygame.font.SysFont('arialbold', 35)
        self.color = 'white'
        self.t1_surfaces, self.t1_rects = self.render_text(
                                    self.settings.p1_controls,
                                    self.font, self.color,
                                    (self.p1_controls_rect.left + 30,
                                    self.p1_controls_rect.top + 30), 25)
        self.t2_surfaces, self.t2_rects = self.render_text(
                                        self.settings.p2_controls,
                                        self.font, self.color,
                                        (self.p2_controls_rect.left + 30,
                                        self.p2_controls_rect.top + 30), 25)


    def render_text(self, text, font, color, start_pos, line_spacing, second_color=None):
        """Render text with new_lines and tabs"""
        lines = text.split('\n')

        text_surfaces = []
        text_rects = []

        tab_width = 10  # Number of spaces per tab

        for i, line in enumerate(lines):
            # Replace tabs with spaces
            line = line.replace('\t', ' ' * tab_width)

            if i  == 0 and second_color:
                text_surface = font.render(line, True, second_color, None)
            else:
                text_surface = font.render(line, True, color, None)

            text_rect = text_surface.get_rect(topleft=(start_pos[0],
                                                        start_pos[1] + i * line_spacing))
            text_surfaces.append(text_surface)
            text_rects.append(text_rect)

        return text_surfaces, text_rects



    def _load_controls_image(self, image_name, position):
        """Loads images for controls displayed on menu screen"""
        image = pygame.image.load(self.button_images[image_name])
        rect = image.get_rect(**position)
        return image, rect


    def _initialize_menu_buttons(self):
        """Create buttons for menu screen"""
        self.single_button = Button(self, self.button_images["single_player"], (0, 0), center=True)
        self.multi_button = Button(self, self.button_images["multiplayer"],
                            (self.single_button.rect.centerx - 100, self.single_button.rect.bottom))
        self.menu_quit_button = Button(self, self.button_images["menu_quit_button"],
                            (self.multi_button.rect.centerx - 100, self.multi_button.rect.bottom))


    def run_menu(self):
        """Runs the menu screen"""
        self.screen = pygame.display.set_mode((self.settings.screen_size))
        while True:
            # Check for mouse click events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.single_button.rect.collidepoint(mouse_x, mouse_y):
                        # Start single player game
                        single_player_game = SingleplayerAlienOnslaught()
                        single_player_game.run_game()
                    elif self.multi_button.rect.collidepoint(mouse_x, mouse_y):
                        # Start multiplayer game
                        multiplayer_game = AlienOnslaught()
                        multiplayer_game.run_game()
                    elif self.menu_quit_button.rect.collidepoint(mouse_x, mouse_y):
                        # Quit menu
                        pygame.quit()
                        sys.exit()

            # Draw the buttons and controls on the screen
            self.screen.blit(self.bg_img, self.bg_img_rect)
            self.single_button.draw_button()
            self.multi_button.draw_button()
            self.menu_quit_button.draw_button()
            self.screen.blit(self.p1_controls, self.p1_controls_rect)
            self.screen.blit(self.p2_controls, self.p2_controls_rect)

            for i, surface in enumerate(self.t1_surfaces):
                self.screen.blit(surface, self.t1_rects[i])

            for i, surface in enumerate(self.t2_surfaces):
                self.screen.blit(surface, self.t2_rects[i])
            pygame.display.flip()


    def _initialize_game_objects(self):
        """Initialize game objects"""
        self.thunderbird_ship = Thunderbird(self, 352, 612)
        self.phoenix_ship = Phoenix(self, 852, 612)
        self.thunderbird_bullets = pygame.sprite.Group()
        self.phoenix_bullets = pygame.sprite.Group()
        self.ships = [self.thunderbird_ship, self.phoenix_ship]
        self.stats = GameStats(self, self.phoenix_ship, self.thunderbird_ship)
        self.score_board = ScoreBoard(self)
        self.alien_bullet = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()


    def _initialize_game_buttons(self):
        """Create buttons for the game"""
        self.play_button = Button(self, self.button_images["play_button"],(0, 0), center=True)
        self.difficulty = Button(self, self.button_images["difficulty"],
                            (self.play_button.rect.centerx - 74, self.play_button.rect.bottom))
        self.game_modes = Button(self, self.button_images["game_modes"],
                            (self.difficulty.rect.centerx - 74, self.difficulty.rect.bottom))
        self.endless_button = Button(self, self.button_images["endless"],
                            (self.game_modes.rect.right - 10, self.game_modes.rect.y))
        self.high_scores = Button(self, self.button_images['high_scores'],
                            (self.game_modes.rect.centerx - 74, self.game_modes.rect.bottom))
        self.menu_button = Button(self, self.button_images["menu_button"],
                            (self.high_scores.rect.centerx - 74, self.high_scores.rect.bottom))
        self.quit_button = Button(self, self.button_images["quit_button"],
                            (self.menu_button.rect.centerx - 74, self.menu_button.rect.bottom))
        self.easy = Button(self, self.button_images['easy'], (self.difficulty.rect.right - 10,
                                                            self.difficulty.rect.y))
        self.medium = Button(self, self.button_images['medium'], (self.easy.rect.right - 5,
                                                            self.easy.rect.y))
        self.hard = Button(self, self.button_images['hard'], (self.medium.rect.right - 5,
                                                            self.medium.rect.y))

    def run_game(self):
        """Main loop for the game."""
        running = True
        i = 0
        while running:
            if not self.paused:  # check if the game is paused
                self._handle_background_change()
                self.screen.blit(self.bg_img, [0,i])
                self.screen.blit(self.bg_img, [0, i  - self.settings.screen_height])
                if i >= self.settings.screen_height:
                    i = 0
                i += 1

                self.check_events()
                self._check_game_over()
                self._check_for_resize()

                if self.stats.game_active:
                    self.endless_game()
                    self._handle_level_tasks()
                    self._create_power_ups()
                    self._update_power_ups()
                    self._update_alien_bullets()
                    self._check_alien_bullets_collisions()
                    self._check_power_ups_collisions()
                    self._update_bullets()
                    self._update_aliens()
                    self.thunderbird_ship.update_state()
                    self.phoenix_ship.update_state()
                    self._shield_collisions(self.ships, self.aliens,
                                             self.alien_bullet, self.asteroids)

                self._update_screen()
                self.clock.tick(60)

            self._check_for_pause()

    def display_high_scores(self):
        """Display the high scores on the screen."""
        # Load the high score data from the JSON file,
        # or create a new high score list if there is an error
        filename = 'high_score.json'
        try:
            with open(filename, 'r', encoding='utf-8') as score_file:
                high_scores = json.load(score_file)
        except json.JSONDecodeError:
            high_scores = {'high_scores': [0] * 10}

        # Get the scores from the high score list and create a new list of tuples
        # containing the score and its rank
        scores = high_scores['high_scores']
        ranked_scores = [(i, score) for i, score in enumerate(scores, 1) if score > 0]

        # Create formatted strings for each rank and score
        rank_strings = [
            f"{('1st' if rank == 1 else '2nd' if rank == 2 else '3rd' if rank == 3 else rank)}:" 
            for rank, score in ranked_scores
        ]
        score_strings = [f"{score}" for rank, score in ranked_scores]

        score_text = "\n".join(score_strings)
        rank_text = "\n".join(rank_strings)

        # Calculate the relative position of the text based on the screen size
        screen_width, screen_height = self.screen.get_size()
        title_x = int(screen_width * 0.065)
        title_y = int(screen_height * 0.35)
        rank_x = int(screen_width * 0.03)
        rank_y = int(screen_height * 0.45)
        score_x = int(screen_width * 0.25)
        score_y = rank_y

        # Render the score text and rank text as surfaces with new lines using different fonts
        font = pygame.font.SysFont('impact', int(screen_height * 0.07))
        text_surfaces, text_rects = self.render_text(
            "HIGH SCORES",
            font,
            'yellow',
            (title_x, title_y),
            int(screen_height * 0.06))

        font = pygame.font.SysFont('impact', int(screen_height * 0.05))
        rank_surfaces, rank_rects = self.render_text(
            rank_text,
            font,
            'red',
            (rank_x, rank_y),
            int(screen_height * 0.05))

        font = pygame.font.SysFont('impact', int(screen_height * 0.05))
        scores_surfaces, scores_rects = self.render_text(
            score_text,
            font,
            'red',
            (score_x, score_y),
            int(screen_height * 0.05))

        # Blit the score text surfaces onto the screen using a loop to avoid repetitive code
        for surfaces, rects in [(text_surfaces, text_rects), (rank_surfaces, rank_rects),
                                 (scores_surfaces, scores_rects)]:
            for surface, rect in zip(surfaces, rects):
                self.screen.blit(surface, rect)

    def check_events(self):
        """Respond to keypresses, mouse and videoresize events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_buttons(mouse_pos)
            elif event.type == pygame.VIDEORESIZE:
                self._resize_screen(event.size)

    def _resize_screen(self, size):
        """Resize the game screen and update relevant game objects."""
        min_width, min_height = 1260, 660
        max_width, max_height = 1920, 1080
        width = max(min(size[0], max_width), min_width)
        height = max(min(size[1], max_height), min_height)
        size = (width, height)
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        self.bg_img = pygame.transform.smoothscale(self.settings.bg_img, self.screen.get_size())
        self.settings.second_bg = pygame.transform.smoothscale(self.settings.second_bg,
                                                                self.screen.get_size())
        self.settings.third_bg = pygame.transform.smoothscale(self.settings.third_bg,
                                                               self.screen.get_size())
        self.reset_bg = pygame.transform.smoothscale(self.settings.bg_img,
                                                      self.screen.get_size())
        self.play_button.update_pos(self.screen.get_rect().center)
        self.difficulty.update_pos(self.play_button.rect.centerx - 74,
                                    self.play_button.rect.bottom)
        self.high_scores.update_pos(self.difficulty.rect.centerx -74,
                                    self.difficulty.rect.bottom)
        self.menu_button.update_pos(self.high_scores.rect.centerx - 74,
                                     self.high_scores.rect.bottom)
        self.quit_button.update_pos(self.menu_button.rect.centerx - 74,
                                     self.menu_button.rect.bottom)
        self.easy.update_pos(self.difficulty.rect.right - 10, self.difficulty.rect.y)
        self.medium.update_pos(self.easy.rect.right - 5, self.difficulty.rect.y)
        self.hard.update_pos(self.medium.rect.right - 5, self.difficulty.rect.y)
        self.score_board.prep_level()
        self.score_board.prep_score()
        self.score_board.prep_high_score()
        self.score_board.prep_hp()
        self._initialize_game_over()
        self.thunderbird_ship.screen_rect = self.screen.get_rect()
        self.phoenix_ship.screen_rect = self.screen.get_rect()


    def _check_keydown_events(self, event):
        """Respond to keys being pressed."""
        match event.key:
            # If the game is paused, check for Q, P, R, and M keys
            case pygame.K_q if self.paused:
                pygame.quit()
                sys.exit()
            case pygame.K_p:
                self.paused = not self.paused
            case pygame.K_r if self.paused:
                self._reset_game()
                self.paused = not self.paused
            case pygame.K_m if self.paused:
                self.run_menu()

            # If the game is not paused, check for player keypresses
            case _ if not self.paused:
                # Thunderbird controls
                if self.thunderbird_ship.alive and not self.thunderbird_ship.is_warping:
                    match event.key:
                        case pygame.K_RIGHT:
                            self.thunderbird_ship.moving_right = True
                        case pygame.K_LEFT:
                            self.thunderbird_ship.moving_left = True
                        case pygame.K_UP:
                            self.thunderbird_ship.moving_up = True
                        case pygame.K_DOWN:
                            self.thunderbird_ship.moving_down = True
                        case pygame.K_RETURN:
                            self._fire_bullet(
                                self.thunderbird_bullets,
                                self.settings.thunderbird_bullets_allowed,
                                bullet_class=Thunderbolt,
                                num_bullets=self.settings.thunderbird_bullet_count,
                                ship=self.thunderbird_ship)
                            self.settings.fire_sound.play()
                        case pygame.K_KP1:
                            self.thunderbird_ship.image = self.thunderbird_ship.ship_images[0]
                        case pygame.K_KP2:
                            self.thunderbird_ship.image = self.thunderbird_ship.ship_images[1]
                        case pygame.K_KP3:
                            self.thunderbird_ship.image = self.thunderbird_ship.ship_images[2]

                # Phoenix controls
                if self.phoenix_ship.alive and not self.phoenix_ship.is_warping:
                    match event.key:
                        case pygame.K_SPACE:
                            self._fire_bullet(
                                self.phoenix_bullets,
                                self.settings.phoenix_bullets_allowed,
                                bullet_class=Firebird,
                                num_bullets=self.settings.phoenix_bullet_count,
                                ship=self.phoenix_ship)
                            self.settings.fire_sound.play()
                        case pygame.K_a:
                            self.phoenix_ship.moving_left = True
                        case pygame.K_d:
                            self.phoenix_ship.moving_right = True
                        case pygame.K_w:
                            self.phoenix_ship.moving_up = True
                        case pygame.K_s:
                            self.phoenix_ship.moving_down = True
                        case pygame.K_1:
                            self.phoenix_ship.image = self.phoenix_ship.ship_images[3]
                        case pygame.K_2:
                            self.phoenix_ship.image = self.phoenix_ship.ship_images[4]
                        case pygame.K_3:
                            self.phoenix_ship.image = self.phoenix_ship.ship_images[5]

                # No active players
            case _:
                self.thunderbird_ship.moving_right = False
                self.thunderbird_ship.moving_left = False
                self.thunderbird_ship.moving_up = False
                self.thunderbird_ship.moving_down = False
                self.phoenix_ship.moving_right = False
                self.phoenix_ship.moving_left = False
                self.phoenix_ship.moving_up = False
                self.phoenix_ship.moving_down = False


    def _check_keyup_events(self, event):
        """Respond to keys being released."""
        # Thunderbird controls
        if self.thunderbird_ship.alive:
            match event.key:
                # Thunderbird controls
                case pygame.K_RIGHT:
                    self.thunderbird_ship.moving_right = False
                case pygame.K_LEFT:
                    self.thunderbird_ship.moving_left = False
                case pygame.K_UP:
                    self.thunderbird_ship.moving_up = False
                case pygame.K_DOWN:
                    self.thunderbird_ship.moving_down = False

            # Phoenix controls
        if self.phoenix_ship.alive:
            match event.key:
                case pygame.K_d:
                    self.phoenix_ship.moving_right = False
                case pygame.K_a:
                    self.phoenix_ship.moving_left = False
                case pygame.K_w:
                    self.phoenix_ship.moving_up = False
                case pygame.K_s:
                    self.phoenix_ship.moving_down = False

        if not self.thunderbird_ship.alive and not self.phoenix_ship.alive:
            self.thunderbird_ship.moving_right = False
            self.thunderbird_ship.moving_left = False
            self.thunderbird_ship.moving_up = False
            self.thunderbird_ship.moving_down = False
            self.phoenix_ship.moving_right = False
            self.phoenix_ship.moving_left = False
            self.phoenix_ship.moving_up = False
            self.phoenix_ship.moving_down = False


    def _check_for_pause(self):
        """Check if the game is paused."""
        if self.paused:
            pause_rect = self.settings.pause.get_rect()
            pause_rect.centerx = self.screen.get_rect().centerx
            pause_rect.centery = self.screen.get_rect().centery
            self.screen.blit(self.settings.pause, pause_rect)
            pygame.display.flip()
            while self.paused:
                self.check_events()
                if not self.paused:
                    self._update_screen()
                    break


    def _handle_level_tasks(self):
        """Handle behaviors for different levels."""
        # start creating asteroids when level is 7 or more
        if self.stats.level >= 7:
            self._create_asteroids()
            self._update_asteroids()
            self._check_asteroids_collisions()
        # increase points for different bosses
        if self.stats.level == 15:
            self.settings.boss_points = 5000
        elif self.stats.level == 20:
            self.settings.boss_points = 7000
        # bullets for boss fights
        if self.stats.level in [10, 15, 20]:
            self._create_alien_bullets(1, 500, 500)
        # bullets for the normal game
        else:
            self._create_alien_bullets(4, 4500, 7000)


    def _handle_background_change(self):
        """Change the background for different levels."""
        bg_images = {
            1: self.reset_bg,
            6: self.settings.second_bg,
            12: self.settings.third_bg,
        }
        self.bg_img = bg_images.get(self.stats.level, self.bg_img)


    def _handle_alien_creation(self):
        """Choose what aliens to create"""
        # boss fights
        if self.stats.level in [9, 14, 19]:
            self._create_boss_alien()
        # normal game
        else:
            self._create_fleet()


    def _check_for_resize(self):
        """Choose when the window is resizable."""
        # the game window is resizable before clicking the Play button
        # players can't resize the window while the game is active.
        info = pygame.display.Info()
        if not self.stats.game_active and not self.resizable:
            pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            self.resizable = True
        elif self.stats.game_active and self.resizable:
            pygame.display.set_mode((info.current_w, info.current_h))
            self.resizable = False


    def _fire_bullet(self, bullets, bullets_allowed, bullet_class, num_bullets, ship):
        """Create new player bullets."""
        # Create the bullets at and position them correctly as the number of bullets increases
        if len(bullets) < bullets_allowed:
            if ship.bullet_power:
                for i in range(num_bullets):
                    new_bullet = bullet_class(self)
                    bullets.add(new_bullet)
                    offset_amount = 25
                    offset_x = offset_amount * (i - (num_bullets - 1) / 2)
                    offset_y = offset_amount * (i - (num_bullets - 1) / 2)
                    new_bullet.rect.centerx = ship.rect.centerx + offset_x
                    new_bullet.rect.centery = ship.rect.centery + offset_y
            else:
                new_bullet = bullet_class(self)
                new_bullet.rect.centerx = ship.rect.centerx
                new_bullet.rect.centery = ship.rect.centery - 30
                bullets.add(new_bullet)


    def _update_bullets(self):
        """Update position of bullets and get rid of bullets that went of screen."""
        self.thunderbird_bullets.update()
        self.phoenix_bullets.update()

        # Get rid of bullets that went off screen.
        for bullet in self.thunderbird_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.thunderbird_bullets.remove(bullet)

        for bullet in self.phoenix_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.phoenix_bullets.remove(bullet)
        # check for collisions between aliens and bullets
        self._check_bullet_alien_collisions()


    def _update_asteroids(self):
        """Update asteroids and remove asteroids that went off screen."""
        self.asteroids.update()
        for asteroid in self.asteroids.copy():
            if asteroid.rect.bottom <= 0:
                self.asteroids.remove(asteroid)


    def _update_power_ups(self):
        """Update power-ups and remove power ups that went off screen."""
        self.power_ups.update()
        for power in self.power_ups.copy():
            if power.rect.bottom <= 0:
                self.power_ups.remove(power)


    def _update_alien_bullets(self):
        """Update alien bullets and remove bullets that went off screen"""
        self.alien_bullet.update()
        for bullet in self.alien_bullet.copy():
            if bullet.rect.bottom <= 0:
                self.alien_bullet.remove(bullet)


    def _update_stats(self, alien, player):
        """Update player score and remove alien"""
        # when collision happen, update the stats and remove the alien that
        # collided with the bullet
        # method used in _handle_player_collisions
        match player:
            case 'thunderbird':
                self.stats.score += self.settings.alien_points
            case 'phoenix':
                self.stats.second_score += self.settings.alien_points
        self.aliens.remove(alien)
        self.score_board.prep_score()
        self.score_board.check_high_score()


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        thunderbird_ship_collisions = pygame.sprite.groupcollide(
            self.thunderbird_bullets, self.aliens, True, False)
        phoenix_ship_collisions = pygame.sprite.groupcollide(
            self.phoenix_bullets, self.aliens, True, False)

        # Thunderbird collisions
        if self.thunderbird_ship.alive and thunderbird_ship_collisions:
            self._handle_player_collisions(thunderbird_ship_collisions, 'thunderbird')

        # Phoenix collisions
        if self.phoenix_ship.alive and phoenix_ship_collisions:
            self._handle_player_collisions(phoenix_ship_collisions, 'phoenix')

        # The player kills all aliens and finishes the level
        if not self.aliens:
            self._handle_alien_creation()
            self.thunderbird_bullets.empty()
            self.phoenix_bullets.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.asteroids.empty()
            self.settings.increase_speed()
            self.stats.level += 1
            self.score_board.prep_level()


    def _handle_player_collisions(self, player_ship_collisions, player):
        for aliens in player_ship_collisions.values():
            for alien in aliens:
                alien.hit_count += 1
                if isinstance(alien, BossAlien):
                    if alien.hit_count >= self.settings.boss_hp:
                        self.aliens.remove(alien)
                        if player == 'thunderbird':
                            self.stats.score += self.settings.boss_points
                        else:
                            self.stats.second_score += self.settings.boss_points
                        self.score_board.prep_score()
                        self.score_board.check_high_score()
                else:
                    if self.stats.level < 5:
                        if alien.hit_count >= 1:
                            self._update_stats(alien, player)
                    elif self.stats.level < 10:
                        if alien.hit_count >= 2:
                            self._update_stats(alien, player)
                    else:
                        if alien.hit_count >= 3:
                            self._update_stats(alien, player)


    def _create_power_ups(self):
        """Create multiple power ups after a certain time has passed"""
        if self.last_power_up_time == 0:
            self.last_power_up_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        # change the range to determine how often power ups are created
        if current_time - self.last_power_up_time >= random.randint(15000, 45000): # miliseconds
            self.last_power_up_time = current_time
            # change the range to determine the chance for a power up to be health power up
            if random.randint(0, 4) == 0:
                power_up = HealthPowerUp(self)
            else:
                power_up = PowerUp(self)
            # create power up at a random location, at the top of the screen.
            power_up.rect.x = random.randint(0, self.settings.screen_width - power_up.rect.width)
            power_up.rect.y = random.randint(-100, -40)
            self.power_ups.add(power_up)


    def _create_asteroids(self):
        """Create multiple asteroids"""
        if self.last_asteroid_time == 0:
            self.last_asteroid_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        # change the range to determine how often asteroids are created.
        if current_time - self.last_asteroid_time >= random.randint(4000, 10000): # miliseconds
            self.last_asteroid_time = current_time
            # create asteroid at a random location, at the top of the screen.
            asteroid = Asteroid(self)
            asteroid.rect.x = random.randint(0, self.settings.screen_width - asteroid.rect.width)
            asteroid.rect.y = random.randint(-100, -40)
            self.asteroids.add(asteroid)


    def _check_power_ups_collisions(self):
        """Check for collision between ships and power-ups
        If a collision occurs, a random power up is activated for the coresponding player
        and the power up is removed.
        """
        # Define a dict that maps each player to their corresponding ship,
        # active status, and power-up functions
        player_info = {
            "thunderbird": {
                "ship": self.thunderbird_ship,
                "active": self.thunderbird_ship.alive,
                "power_up": self._power_up_player,
                "health_power_up": self._health_power_up,
            },
            "phoenix": {
                "ship": self.phoenix_ship,
                "active": self.phoenix_ship.alive,
                "power_up": self._power_up_player,
                "health_power_up": self._health_power_up,
            },
        }
        # loop through each player and check for collisions
        for player, info in player_info.items():
            collision = pygame.sprite.spritecollideany(info["ship"], self.power_ups)
            if info["active"] and collision:
                # check the type of the power up and activate the func
                if isinstance(collision, PowerUp):
                    info["power_up"](player)
                elif isinstance(collision, HealthPowerUp):
                    info["health_power_up"](player)
                collision.kill()


    def _check_asteroids_collisions(self):
        """Check for collisions between the ships and asteroids"""
        # loop through each player and check if it's alive,
        # then check for collisions with asteroids and which player collided
        # and activate the corresponding method
        for ship in self.ships:
            if ship.alive:
                collision = pygame.sprite.spritecollideany(ship, self.asteroids)
                if collision:
                    if ship is self.thunderbird_ship:
                        self._thunderbird_ship_hit()
                    else:
                        self._phoenix_ship_hit()
                    collision.kill()


    def _shield_collisions(self, ships, aliens, bullets, asteroids):
        """Destroy any aliens that collide with the shield of any of the given ships."""
        # Loop through each player and check if the shield is on, if it is, kill the
        # alien, alien bullet or asteroid that collided with it and turn the shield off.
        for ship in ships:
            for alien in aliens:
                if ship.shield_on and ship.shield_rect.colliderect(alien.rect):
                    alien.kill()
                    ship.shield_on = False
            for bullet in bullets:
                if ship.shield_on and ship.shield_rect.colliderect(bullet.rect):
                    bullet.kill()
                    ship.shield_on = False
            for asteroid in asteroids:
                if ship.shield_on and ship.shield_rect.colliderect(asteroid):
                    asteroid.kill()
                    ship.shield_on = False


    def _power_up_player(self, player):
        """Powers up the specified player"""
        # each lambda function performs a different power up on the player.
        power_up_choices = [
            lambda: setattr(self.settings, f"{player}_ship_speed",
                             getattr(self.settings, f"{player}_ship_speed") + 0.3),
            lambda: setattr(self.settings, f"{player}_bullet_speed",
                             getattr(self.settings, f"{player}_bullet_speed") + 0.3),
            lambda: setattr(self.settings, f"{player}_bullets_allowed",
                             getattr(self.settings, f"{player}_bullets_allowed") + 2),
            lambda: setattr(self.settings, f"{player}_bullet_count",
                             getattr(self.settings, f"{player}_bullet_count") + 1),
            lambda: getattr(self, f"{player}_ship").draw_shield(),
        ]
        # randomly select one of the power ups and activate it.
        power_up_choice = random.choice(power_up_choices)
        power_up_choice()


    def _health_power_up(self, player):
        """Increases the health of the specified player"""
        player_health_attr = {
            "thunderbird": "thunderbird_hp",
            "phoenix": "phoenix_hp",
        }
        if getattr(self.stats, player_health_attr[player]) < self.settings.max_hp:
            setattr(self.stats, player_health_attr[player],
                     getattr(self.stats, player_health_attr[player]) + 1)
        self.score_board.prep_hp()



    def _check_alien_bullets_collisions(self):
        """Manages collisions between the alien bullets and the players"""
        # check for collisions between each player and alien bullet and if a collision
        # occurrs, call the appropriate method and kill the collision.
        thunderbird_collision = pygame.sprite.spritecollideany(self.thunderbird_ship,
                                                                 self.alien_bullet)
        phoenix_collision = pygame.sprite.spritecollideany(self.phoenix_ship,
                                                                  self.alien_bullet)

        if self.thunderbird_ship.alive and thunderbird_collision:
            self._thunderbird_ship_hit()
            thunderbird_collision.kill()

        if self.phoenix_ship.alive and phoenix_collision:
            self._phoenix_ship_hit()
            phoenix_collision.kill()


    def _thunderbird_ship_hit(self):
        """Respond to the Thunderbird ship being hit by an alien, bullet or asteroid."""
        if self.thunderbird_ship.exploding:
            return

        if self.stats.thunderbird_hp > 0:
            # what happens when the player get's hit
            self.thunderbird_ship.explode()
            self.thunderbird_ship.shield_on = False
            self.settings.thunderbird_bullet_count = 1
            if self.settings.thunderbird_bullets_allowed > 1:
                self.settings.thunderbird_bullets_allowed -= 2
            self.stats.thunderbird_hp -= 1

            self.thunderbird_ship.center_ship()
            self.score_board.prep_hp()
        else:
            # player becomes inactive when loses all hp
            self.thunderbird_ship.alive = False
            # if the other player is active, remove bullets and continue
            # until both players are dead
            if self.phoenix_ship.alive:
                self.thunderbird_bullets.empty()
            else:
                # game over if both player are inactive.
                self.stats.game_active = False


    def _phoenix_ship_hit(self):
        """Respond to the Phoenix ship being hit by an alien, bullet or asteroid."""
        if self.phoenix_ship.exploding:
            return

        if self.stats.phoenix_hp > 0:
            # what happens when the player gets hit
            self.phoenix_ship.explode()
            self.phoenix_ship.shield_on = False
            self.settings.phoenix_bullet_count = 1
            if self.settings.phoenix_bullets_allowed > 1:
                self.settings.phoenix_bullets_allowed -= 2
            self.stats.phoenix_hp -= 1

            self.phoenix_ship.center_ship()
            self.score_board.prep_hp()
        else:
            # player becomes inactive when loses all hp
            self.phoenix_ship.alive = False
            # if the other player is active, remove bullets and continue
            # until both players are dead
            if self.thunderbird_ship.alive:
                self.phoenix_bullets.empty()
            else:
                # game over if both players are inactive.
                self.stats.game_active = False


    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        # Calculate the starting y-coordinate for the first row of aliens
        start_y = 50

        # Create the full fleet of aliens.
        for row_number in range(self.settings.fleet_rows):
            for alien_number in range(self.settings.aliens_num):
                # Create the alien and set its starting position above the top of the screen
                alien = Alien(self)
                alien.rect.x = alien_width + 2 * alien_width * alien_number
                alien.rect.y = start_y - (2 * alien_height * row_number)
                # Add the alien to the group of aliens
                self.aliens.add(alien)

    def endless_game(self):
        """Starts the endless game mode in which fleets of aliens and
        asteroids keep coming and the speed of aliens and their bullets increases
        over time."""
        if self.settings.endless and len(self.aliens) < self.settings.endless_num:
            self._create_fleet()

        if self.settings.endless:
            self._create_asteroids()
            self._update_asteroids()
            self._check_asteroids_collisions()

        # Increase alien and bullet speed every 120 seconds
        current_time = time.time()
        if current_time - self.last_increase_time >= 120: # seconds
            self.settings.alien_speed += 0.1
            self.settings.alien_bullet_speed += 0.1
            self.last_increase_time = current_time


    def _create_boss_alien(self):
        """Create a boss alien and add it to the aliens group."""
        boss_alien = BossAlien(self)
        self.aliens.add(boss_alien)



    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.thunderbird_ship, self.aliens):
            self._thunderbird_ship_hit()
        if pygame.sprite.spritecollideany(self.phoenix_ship, self.aliens):
            self._phoenix_ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()


    def _create_alien_bullet(self, alien):
        """Create an alien bullet at the specified alien rect"""
        # create different bullets for bosses
        if isinstance(alien, BossAlien):
            bullet = BossBullet(self, alien)
        else:
            bullet = AlienBullet(self)
        bullet.rect.centerx = alien.rect.centerx
        bullet.rect.bottom = alien.rect.bottom
        self.alien_bullet.add(bullet)


    def _create_alien_bullets(self, num_bullets, bullet_int, alien_int):
        """Create a certain number of bullets at a certain time.
        bullet_int - for adjusting how often aliens fire bullets.
        alien_int - for adjusting how often a specific alien fires a bullet.
        """
        current_time = pygame.time.get_ticks()
        # calculate the time since any alien fired a bullet
        if current_time - self.last_alien_bullet_time >= bullet_int:
            self.last_alien_bullet_time = current_time
            aliens = random.sample(self.aliens.sprites(), k=min(num_bullets,
                                                                 len(self.aliens.sprites())))
            for alien in aliens:
                # calculate the time since a specific alien fired a bullet
                if alien.last_bullet_time == 0 or current_time - alien.last_bullet_time >= alien_int:
                    alien.last_bullet_time = current_time
                    self._create_alien_bullet(alien)


    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """Change the direction of each alien and drop them down."""
        # bosses are not moving down
        for alien in self.aliens.sprites():
            if isinstance(alien, BossAlien):
                if alien.check_edges():
                    alien.direction *= -1
                else:
                    alien.rect.x += (self.settings.alien_speed *
                                     alien.direction)
            else:
                if alien.check_edges():
                    alien.direction *= -1

                elif alien.check_top_edges():
                    alien.rect.y += self.settings.alien_speed


    def _check_aliens_bottom(self):
        """Check if an alien have reached the bottom of the screen"""
        # if an alien reaches the bottom of the screen, both players are losing 1hp
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._thunderbird_ship_hit()
                self._phoenix_ship_hit()
                break

    def _check_game_over(self):
        """Check if the game is over and if so, display the game over image"""
        if not any([self.stats.game_active, self.thunderbird_ship.alive,
                     self.phoenix_ship.alive]):
            self.screen.blit(self.settings.game_over, self.game_over_rect)
            self.aliens.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.score_board.check_high_score()
            if not self.high_score_saved:
                self.score_board.save_high_score()
                self.high_score_saved = True


    def _initialize_game_over(self):
        """Set the location of the game over image on the screen"""
        game_over_rect = self.settings.game_over.get_rect()
        game_over_x = (self.settings.screen_width - game_over_rect.width) / 2
        game_over_y = (self.settings.screen_height - game_over_rect.height) / 2 - 100
        self.game_over_rect = pygame.Rect(game_over_x, game_over_y,
                                        game_over_rect.width, game_over_rect.height)


    def _load_button_images(self, button_names):
        """Load button images"""
        button_images = {}
        for name in button_names:
            filename = f"images/buttons/{name}.png"
            button_images[name] = filename
        return button_images


    def _check_buttons(self, mouse_pos):
        """Check for buttons being clicked and act accordingly."""
        buttons = {
            self.play_button: lambda: (self._reset_game(),
                                       setattr(self, 'show_difficulty', False),
                                       setattr(self, 'show_high_scores', False),
                                       setattr(self, 'show_game_modes', False)),
            self.quit_button: lambda: (pygame.quit(), sys.exit()),
            self.menu_button: self.run_menu,
            self.high_scores: lambda: setattr(self, 'show_high_scores', not self.show_high_scores),
            self.game_modes: lambda: setattr(self, 'show_game_modes', not self.show_game_modes),
            self.endless_button: lambda: (setattr(self.settings, 'endless', not self.settings.endless),
                                           setattr(self, 'show_game_modes', False)),
            self.easy: lambda: (setattr(self.settings, 'speedup_scale', 0.3),
                                 setattr(self, 'show_difficulty', False)),
            self.medium: lambda: (setattr(self.settings, 'speedup_scale', 0.5),
                                   setattr(self, 'show_difficulty', False)),
            self.hard: lambda: (setattr(self.settings, 'speedup_scale', 0.7),
                                 setattr(self, 'show_difficulty', False)),
            self.difficulty: lambda: setattr(self, 'show_difficulty', not self.show_difficulty),
        }
        for button, action in buttons.items():
            if button.rect.collidepoint(mouse_pos) and not self.stats.game_active:
                action()



    def _reset_game(self):
        # Reset the game statistics.
        self.stats.reset_stats(self.phoenix_ship, self.thunderbird_ship)
        self.settings.initialize_dynamic_settings()
        self.stats.game_active = True
        self.high_score_saved = False
        self.score_board.prep_score()
        self.score_board.prep_level()
        self.score_board.prep_hp()

        # Get rid of remaining aliens, bullets, asteroids and power-ups.
        self.thunderbird_bullets.empty()
        self.phoenix_bullets.empty()
        self.alien_bullet.empty()
        self.power_ups.empty()
        self.aliens.empty()
        self.asteroids.empty()

        # Create a new fleet, play the warp animation and center the ships.
        self.thunderbird_ship.start_warp()
        self.phoenix_ship.start_warp()
        self.thunderbird_ship.center_ship()
        self.phoenix_ship.center_ship()
        self._create_fleet()


    def _update_screen(self):
        """Update images on the screen"""
        # Draw game objects if game is active
        if self.stats.game_active:
            self.thunderbird_ship.blitme()
            self.phoenix_ship.blitme()

            for bullet in self.thunderbird_bullets.sprites():
                bullet.draw_bullet()

            for bullet in self.phoenix_bullets.sprites():
                bullet.draw_bullet()

            for bullet in self.alien_bullet.sprites():
                bullet.draw_bullet()

            for power_up in self.power_ups.sprites():
                power_up.draw_powerup()

            for asteroid in self.asteroids.sprites():
                asteroid.draw_asteroid()

            self.aliens.draw(self.screen)
            self.score_board.show_score()

        # Draw buttons if game is not active
        else:
            self.play_button.draw_button()
            self.quit_button.draw_button()
            self.menu_button.draw_button()
            self.difficulty.draw_button()
            self.high_scores.draw_button()
            self.game_modes.draw_button()

            # Draw difficulty buttons if difficulty menu is shown
            if self.show_difficulty:
                self.easy.draw_button()
                self.medium.draw_button()
                self.hard.draw_button()

            if self.show_high_scores:
                self.display_high_scores()

            if self.show_game_modes:
                self.endless_button.draw_button()

        pygame.display.flip()



class SingleplayerAlienOnslaught(AlienOnslaught):
    """A class that manages the Singleplayer version of the game"""
    def __init__(self):
        super().__init__()
        self.score_board = SecondScoreBoard(self)
        self.clock = pygame.time.Clock()
        self.thunderbird_ship = Thunderbird(self, 602, 612)
        self.thunderbird_ship.single_player = True
        self.ships = [self.thunderbird_ship]


    def run_game(self):
        """Main loop of the game"""
        running = True
        i = 0
        while running:
            if not self.paused:
                self._handle_background_change()
                self.screen.blit(self.bg_img, [0,i])
                self.screen.blit(self.bg_img, [0, i  - self.settings.screen_height])
                if i >= self.settings.screen_height:
                    i = 0
                i += 1

                self.check_events()
                self._check_game_over()
                self._check_for_resize()

                if self.stats.game_active:
                    self.endless_game()
                    self._handle_level_tasks()
                    self._create_power_ups()
                    self._update_power_ups()
                    self._update_alien_bullets()
                    self._check_alien_bullets_collisions()
                    self._check_power_ups_collisions()
                    self._update_bullets()
                    self._update_aliens()
                    self.thunderbird_ship.update_state()
                    self._shield_collisions(self.ships, self.aliens,
                                             self.alien_bullet, self.asteroids)

                self.clock.tick(60)
                self._update_screen()
            self._check_for_pause()


    def _check_keydown_events(self, event):
        """Respod to keypresses."""
        match event.key:
            # If the game is paused, check for Q, P, R, and M keys
            case pygame.K_q if self.paused:
                sys.exit()
            case pygame.K_p:
                self.paused = not self.paused
            case pygame.K_r if self.paused:
                self._reset_game()
                self.paused = not self.paused
            case pygame.K_m if self.paused:
                self.run_menu()

            case _ if not self.paused:
                match event.key:
                    case pygame.K_RIGHT:
                        self.thunderbird_ship.moving_right = True
                    case pygame.K_LEFT:
                        self.thunderbird_ship.moving_left = True
                    case pygame.K_UP:
                        self.thunderbird_ship.moving_up = True
                    case pygame.K_DOWN:
                        self.thunderbird_ship.moving_down = True
                    case pygame.K_RETURN:
                        self._fire_bullet(
                            self.thunderbird_bullets,
                            self.settings.thunderbird_bullets_allowed,
                            bullet_class=Thunderbolt,
                            num_bullets=self.settings.thunderbird_bullet_count,
                            ship=self.thunderbird_ship)
                        self.settings.fire_sound.play()
                    case pygame.K_KP1:
                        self.thunderbird_ship.image = self.thunderbird_ship.ship_images[0]
                    case pygame.K_KP2:
                        self.thunderbird_ship.image = self.thunderbird_ship.ship_images[1]
                    case pygame.K_KP3:
                        self.thunderbird_ship.image = self.thunderbird_ship.ship_images[2]


    def _check_keyup_events(self, event):
        """Respot to key releases."""
        match event.key:
            case pygame.K_RIGHT:
                self.thunderbird_ship.moving_right = False
            case pygame.K_LEFT:
                self.thunderbird_ship.moving_left = False
            case pygame.K_UP:
                self.thunderbird_ship.moving_up = False
            case pygame.K_DOWN:
                self.thunderbird_ship.moving_down = False


    def _reset_game(self):
        # Reset the game statistics.
        self.stats.reset_stats(self.phoenix_ship, self.thunderbird_ship)
        self.settings.initialize_dynamic_settings()
        self.stats.game_active = True
        self.high_score_saved = False
        self.score_board.prep_score()
        self.score_board.prep_level()
        self.score_board.prep_hp()

        # Get rid of the remaining aliens, bullets, asteroids and power ups
        self.thunderbird_bullets.empty()
        self.alien_bullet.empty()
        self.power_ups.empty()
        self.aliens.empty()
        self.asteroids.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.thunderbird_ship.start_warp()
        self.thunderbird_ship.center_ship()


    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.thunderbird_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.thunderbird_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.thunderbird_bullets.remove(bullet)
        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        thunderbird_ship_collisions = pygame.sprite.groupcollide(
            self.thunderbird_bullets, self.aliens, True, False)

        # Player collisions
        if self.thunderbird_ship.alive and thunderbird_ship_collisions:
            self._handle_player_collisions(thunderbird_ship_collisions, 'thunderbird')

        if not self.aliens:
            self._handle_alien_creation()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.asteroids.empty()
            self.thunderbird_bullets.empty()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.score_board.prep_level()


    def _thunderbird_ship_hit(self):
        """Respond to the Thunderbird ship being hit by an alien."""
        if self.thunderbird_ship.exploding:
            return

        if self.stats.thunderbird_hp > 0:
            self.thunderbird_ship.explode()
            self.thunderbird_ship.shield_on = False
            self.settings.thunderbird_bullet_count = 1
            if self.settings.thunderbird_bullets_allowed > 1:
                self.settings.thunderbird_bullets_allowed -= 2
            self.stats.thunderbird_hp -= 1
            self.thunderbird_ship.center_ship()
            self.score_board.prep_hp()
        else:
            self.thunderbird_ship.alive = False
            self.stats.game_active = False

    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.thunderbird_ship, self.aliens):
            self._thunderbird_ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()


    def _check_game_over(self):
        """Check if the game is over, if so, display the game over image"""
        if not self.stats.game_active and not self.thunderbird_ship.alive:
            self.screen.blit(self.settings.game_over, self.game_over_rect)
            self.aliens.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.score_board.check_high_score()
            if not self.high_score_saved:
                self.score_board.save_high_score()
                self.high_score_saved = True


    def _update_screen(self):
        """Update images on the screen."""
        # Draw game objects if the game is active.
        if self.stats.game_active:
            self.thunderbird_ship.blitme()

            for bullet in self.thunderbird_bullets.sprites():
                bullet.draw_bullet()

            for power_up in self.power_ups.sprites():
                power_up.draw_powerup()

            for bullet in self.alien_bullet.sprites():
                bullet.draw_bullet()

            for asteroid in self.asteroids.sprites():
                asteroid.draw_asteroid()

            self.aliens.draw(self.screen)
            # Draw the score information.
            self.score_board.show_score()

        # Draw the buttons if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.quit_button.draw_button()
            self.menu_button.draw_button()
            self.high_scores.draw_button()
            self.difficulty.draw_button()
            self.game_modes.draw_button()

            if self.show_difficulty:
                self.easy.draw_button()
                self.medium.draw_button()
                self.hard.draw_button()

            if self.show_high_scores:
                self.display_high_scores()

            if self.show_game_modes:
                self.endless_button.draw_button()


        pygame.display.flip()


if __name__ =='__main__':
    start = AlienOnslaught()
    start.run_menu()
