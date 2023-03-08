"""
The Alien Onslaught game module contains the multiplayer and singleplayer versions of the game.
This module imports all other classes and modules required to run the game.
In this game the players have to shoot fleets of aliens in order to
reach higher levels and increase their high score.


Author: [Miron Alexandru]
Date: 
"""
import sys
import random
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
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        self.bg_img = pygame.transform.smoothscale(self.settings.bg_img, self.screen.get_size())
        self.bg_img_rect = self.bg_img.get_rect()
        self.reset_bg = pygame.transform.smoothscale(self.settings.bg_img, self.screen.get_size())
        self.second_bg = self.settings.second_bg
        self.third_bg = self.settings.third_bg
        self.fire_sound = self.settings.fire_sound
        self.last_power_up_time = 0
        self.last_alien_bullet_time = 0
        self.last_asteroid_time = 0
        self.button_names = ["play_button", "quit_button", "menu_button",
                            'difficulty', 'easy', 'medium', 'hard']
        self.button_images = self._load_button_images(self.button_names)
        self.game_over = self.settings.game_over
        self.pause_img = self.settings.pause
        self.paused = False
        self.show_difficulty = False
        self.resizable = True


        self._initialize_game_objects()
        self._initialize_game_buttons()
        self._initialize_game_over()
        self._initialize_start_menu()
        self._initialize_menu_buttons()

        pygame.display.set_caption("Alien Onslaught")


    def _initialize_start_menu(self):
        """Initializes variables for the start menu"""
        self.button_names = ["single_player", "multiplayer",
                            "player_controls", "menu_quit_button",]
        self.button_images = self._load_button_images(self.button_names)

        self.p1_controls, self.p1_controls_rect = self._load_controls_image(
                                                'player_controls',
                                                {'topleft': (50, 50)})
        self.p2_controls, self.p2_controls_rect = self._load_controls_image(
                                                'player_controls',
                                                {'topright':
                                                (self.settings.screen_width - 50, 50)})

        self.font = pygame.font.SysFont('arialbold', 35)
        self.color = (255, 255, 255)
        self.t1_surfaces, self.t1_rects = self.render_text(
                                    self.settings.p1_controls,
                                    self.font, self.color,
                                    (self.p1_controls_rect.left + 30,
                                    self.p1_controls_rect.top + 30))
        self.t2_surfaces, self.t2_rects = self.render_text(
                                        self.settings.p2_controls,
                                        self.font, self.color,
                                        (self.p2_controls_rect.left + 30,
                                        self.p2_controls_rect.top + 30))


    def render_text(self, text, font, color, start_pos):
        """Render text with new_lines"""
        lines = text.split('\n')

        text_surfaces = []
        text_rects = []

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color, None)
            text_rect = text_surface.get_rect(topleft=(start_pos[0], start_pos[1] + i * 25))
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
        self.first_player_ship = Thunderbird(self, 352, 612)
        self.second_player_ship = Phoenix(self, 852, 612)
        self.ships = [self.first_player_ship, self.second_player_ship]
        self.stats = GameStats(self)
        self.second_stats = GameStats(self)
        self.score_board = ScoreBoard(self)
        self.first_player_bullets = pygame.sprite.Group()
        self.second_player_bullets = pygame.sprite.Group()
        self.alien_bullet = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()


    def _initialize_game_buttons(self):
        """Create buttons for the game"""
        self.play_button = Button(self, self.button_images["play_button"],(0, 0), center=True)
        self.difficulty = Button(self, self.button_images["difficulty"],
                            (self.play_button.rect.centerx - 74, self.play_button.rect.bottom))
        self.menu_button = Button(self, self.button_images["menu_button"],
                            (self.difficulty.rect.centerx - 74, self.difficulty.rect.bottom))
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
                    self._handle_level_tasks()
                    self._create_power_ups()
                    self._update_power_ups()
                    self._update_alien_bullets()
                    self._check_alien_bullets_collisions()
                    self._check_power_ups_collisions()
                    self._update_bullets()
                    self._update_aliens()
                    self.first_player_ship.update_state()
                    self.second_player_ship.update_state()
                    self._shield_collisions(self.ships, self.aliens,
                                             self.alien_bullet, self.asteroids)

                self._update_screen()
                self.clock.tick(60)

            self._check_for_pause()


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
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.settings.screen_width = self.screen.get_rect().width
                self.settings.screen_height = self.screen.get_rect().height
                self.bg_img = pygame.transform.smoothscale(self.settings.bg_img,
                                                            self.screen.get_size())
                self.second_bg = pygame.transform.smoothscale(self.settings.second_bg,
                                                                   self.screen.get_size())
                self.third_bg = pygame.transform.smoothscale(self.settings.third_bg,
                                                                    self.screen.get_size())
                self.reset_bg = pygame.transform.smoothscale(self.settings.bg_img,
                                                                  self.screen.get_size())
                self.play_button.update_pos(self.screen.get_rect().center)
                self.difficulty.update_pos(self.play_button.rect.centerx - 74,
                                            self.play_button.rect.bottom)
                self.menu_button.update_pos(self.difficulty.rect.centerx - 74,
                                            self.difficulty.rect.bottom)
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
                self.first_player_ship.screen_rect = self.screen.get_rect()
                self.second_player_ship.screen_rect = self.screen.get_rect()


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
                # Player 1 controls
                if self.stats.player_one_active and not self.first_player_ship.is_warping:
                    match event.key:
                        case pygame.K_RIGHT:
                            self.first_player_ship.moving_right = True
                        case pygame.K_LEFT:
                            self.first_player_ship.moving_left = True
                        case pygame.K_UP:
                            self.first_player_ship.moving_up = True
                        case pygame.K_DOWN:
                            self.first_player_ship.moving_down = True
                        case pygame.K_RETURN:
                            self._fire_bullet(
                                self.first_player_bullets,
                                self.settings.first_player_bullets_allowed,
                                bullet_class=Thunderbolt,
                                num_bullets=self.settings.thunder_bullet_count,
                                ship=self.first_player_ship)
                            self.fire_sound.play()
                        case pygame.K_KP1:
                            self.first_player_ship.image = self.first_player_ship.ship_images[0]
                        case pygame.K_KP2:
                            self.first_player_ship.image = self.first_player_ship.ship_images[1]
                        case pygame.K_KP3:
                            self.first_player_ship.image = self.first_player_ship.ship_images[2]

                # Player 2 controls
                if self.stats.player_two_active and not self.second_player_ship.is_warping:
                    match event.key:
                        case pygame.K_SPACE:
                            self._fire_bullet(
                                self.second_player_bullets,
                                self.settings.second_player_bullets_allowed,
                                bullet_class=Firebird,
                                num_bullets=self.settings.fire_bullet_count,
                                ship=self.second_player_ship)
                            self.fire_sound.play()
                        case pygame.K_a:
                            self.second_player_ship.moving_left = True
                        case pygame.K_d:
                            self.second_player_ship.moving_right = True
                        case pygame.K_w:
                            self.second_player_ship.moving_up = True
                        case pygame.K_s:
                            self.second_player_ship.moving_down = True
                        case pygame.K_1:
                            self.second_player_ship.image = self.second_player_ship.ship_images[3]
                        case pygame.K_2:
                            self.second_player_ship.image = self.second_player_ship.ship_images[4]
                        case pygame.K_3:
                            self.second_player_ship.image = self.second_player_ship.ship_images[5]

                # No active players
            case _:
                self.first_player_ship.moving_right = False
                self.first_player_ship.moving_left = False
                self.first_player_ship.moving_up = False
                self.first_player_ship.moving_down = False
                self.second_player_ship.moving_right = False
                self.second_player_ship.moving_left = False
                self.second_player_ship.moving_up = False
                self.second_player_ship.moving_down = False


    def _check_keyup_events(self, event):
        """Respond to keys being released."""
        # Player 1 controls
        if self.stats.player_one_active:
            match event.key:
                # Player 1 controls
                case pygame.K_RIGHT:
                    self.first_player_ship.moving_right = False
                case pygame.K_LEFT:
                    self.first_player_ship.moving_left = False
                case pygame.K_UP:
                    self.first_player_ship.moving_up = False
                case pygame.K_DOWN:
                    self.first_player_ship.moving_down = False

            # Player 2 controls
        if self.stats.player_two_active:
            match event.key:
                case pygame.K_d:
                    self.second_player_ship.moving_right = False
                case pygame.K_a:
                    self.second_player_ship.moving_left = False
                case pygame.K_w:
                    self.second_player_ship.moving_up = False
                case pygame.K_s:
                    self.second_player_ship.moving_down = False

        if not self.stats.player_one_active and not self.stats.player_two_active:
            self.first_player_ship.moving_right = False
            self.first_player_ship.moving_left = False
            self.first_player_ship.moving_up = False
            self.first_player_ship.moving_down = False
            self.second_player_ship.moving_right = False
            self.second_player_ship.moving_left = False
            self.second_player_ship.moving_up = False
            self.second_player_ship.moving_down = False


    def _check_for_pause(self):
        """Check if the game is paused."""
        if self.paused:
            self.screen.blit(self.pause_img, (300, 150))
            pygame.display.flip()
            while self.paused:
                self.check_events()
                if not self.paused:
                    self._update_screen()
                    break


    def _handle_level_tasks(self):
        """Handle behaviors for different levels."""
        if self.stats.level >= 7:
            self._create_asteroids()
            self._update_asteroids()
            self._check_asteroids_collisions()

        if self.stats.level in [10, 15, 20]:
            self._create_alien_bullets(1, 500, 500)
        else:
            self._create_alien_bullets(4, 4500, 7000)


    def _handle_background_change(self):
        """Change the background for different levels."""
        if self.stats.level <= 1:
            self.bg_img = self.reset_bg
        elif self.stats.level == 6:
            self.bg_img = self.second_bg
        elif self.stats.level >= 12:
            self.bg_img = self.third_bg


    def _handle_alien_creation(self):
        """Choose what aliens to create"""
        if self.stats.level in [9, 14, 19]:
            self._create_boss_alien()
        else:
            self._create_fleet()


    def _check_for_resize(self):
        """Choose when the window is resizable."""
        info = pygame.display.Info()
        if not self.stats.game_active and not self.resizable:
            pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            self.resizable = True
        elif self.stats.game_active and self.resizable:
            pygame.display.set_mode((info.current_w, info.current_h))
            self.resizable = False


    def _fire_bullet(self, bullets, bullets_allowed, bullet_class, num_bullets, ship):
        """Create new player bullets."""
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
        self.first_player_bullets.update()
        self.second_player_bullets.update()

        # Get rid of bullets that went off screen.
        for bullet in self.first_player_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.first_player_bullets.remove(bullet)

        for bullet in self.second_player_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.second_player_bullets.remove(bullet)

        self._check_bullet_alien_collisions()


    def _update_asteroids(self):
        """Update asteroids and remove asteroids that went off screen."""
        self.asteroids.update()
        for asteroid in self.asteroids.copy():
            if asteroid.rect.bottom <=0:
                self.asteroids.remove(asteroid)


    def _update_power_ups(self):
        """Update power-ups and remove power ups that went off screen."""
        self.power_ups.update()
        for power in self.power_ups.copy():
            if power.rect.bottom <=0:
                self.power_ups.remove(power)


    def _update_alien_bullets(self):
        """Update alien bullets and remove bullets that went off screen"""
        self.alien_bullet.update()
        for bullet in self.alien_bullet.copy():
            if bullet.rect.bottom <= 0:
                self.alien_bullet.remove(bullet)


    def _update_stats(self, alien, player):
        """Update player score and remove alien"""
        match player:
            case 'player_1':
                self.stats.score += self.settings.alien_points
            case 'player_2':
                self.second_stats.second_score += self.settings.alien_points
        self.aliens.remove(alien)
        self.score_board.prep_score()
        self.score_board.check_high_score()


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        first_player_ship_collisions = pygame.sprite.groupcollide(
            self.first_player_bullets, self.aliens, True, False)
        second_player_ship_collisions = pygame.sprite.groupcollide(
            self.second_player_bullets, self.aliens, True, False)

        # First player collisions
        if self.stats.player_one_active and first_player_ship_collisions:
            for aliens in first_player_ship_collisions.values():
                for alien in aliens:
                    alien.hit_count += 1
                    if isinstance(alien, BossAlien):
                        if alien.hit_count >= self.settings.boss_hp:
                            self.aliens.remove(alien)
                            self.stats.score += self.settings.boss_points
                            self.score_board.prep_score()
                            self.score_board.check_high_score()
                    else:
                        if self.stats.level < 5:
                            if alien.hit_count >= 1:
                                self._update_stats(alien, 'player_1')
                        elif self.stats.level < 10:
                            if alien.hit_count >= 2:
                                self._update_stats(alien, 'player_1')
                        else:
                            if alien.hit_count >= 3:
                                self._update_stats(alien, 'player_1')

        # Second player collisions
        if self.stats.player_two_active and second_player_ship_collisions:
            for aliens in second_player_ship_collisions.values():
                for alien in aliens:
                    alien.hit_count += 1
                    if isinstance(alien, BossAlien):
                        if alien.hit_count >= self.settings.boss_hp:
                            self.aliens.remove(alien)
                            self.second_stats.second_score += self.settings.boss_points
                            self.score_board.prep_score()
                            self.score_board.check_high_score()
                    else:
                        if self.stats.level < 5:
                            if alien.hit_count >= 1:
                                self._update_stats(alien, 'player_2')
                        elif self.stats.level < 10:
                            if alien.hit_count >= 2:
                                self._update_stats(alien, 'player_2')
                        else:
                            if alien.hit_count >= 3:
                                self._update_stats(alien, 'player_2')

        # The player kills all aliens and finishes the level
        if not self.aliens:
            self._handle_alien_creation()
            self.first_player_bullets.empty()
            self.second_player_bullets.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.asteroids.empty()
            self.settings.increase_speed()
            self.stats.level += 1
            self.score_board.prep_level()


    def _create_asteroid(self):
        """Create an asteroid at a random location and add it to the asteroids group"""
        asteroid = Asteroid(self)
        asteroid.rect.x = random.randint(0, self.settings.screen_width - asteroid.rect.width)
        asteroid.rect.y = random.randint(-100, -40)
        self.asteroids.add(asteroid)


    def _create_power_ups(self):
        """Create multiple power ups after a certain time has passed"""
        if self.last_power_up_time == 0:
            self.last_power_up_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_power_up_time >= random.randint(15000, 45000):
            self.last_power_up_time = current_time
            self._create_power_up()


    def _create_asteroids(self):
        """Create multiple asteroids"""
        if self.last_asteroid_time == 0:
            self.last_asteroid_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_asteroid_time >= random.randint(4000, 10000):
            self.last_asteroid_time = current_time
            self._create_asteroid()


    def _check_power_ups_collisions(self):
        """Check for collision between ship and a power-up"""
        first_player_collision = pygame.sprite.spritecollideany(self.first_player_ship,
                                                                 self.power_ups)
        second_player_collision = pygame.sprite.spritecollideany(self.second_player_ship,
                                                                 self.power_ups)

        # First player collisions
        if self.stats.player_one_active and first_player_collision:
            if isinstance(first_player_collision, PowerUp):
                self._first_ship_power_up()
            elif isinstance(first_player_collision, HealthPowerUp):
                self._first_health_power_up()
            first_player_collision.kill()

        # Second player collisions
        if self.stats.player_two_active and second_player_collision:
            if isinstance(second_player_collision, PowerUp):
                self._second_ship_power_up()
            elif isinstance(second_player_collision, HealthPowerUp):
                self._second_health_power_up()
            second_player_collision.kill()


    def _check_asteroids_collisions(self):
        """Check for collisions betweeen the ships and asteroids"""
        first_player_collision = pygame.sprite.spritecollideany(self.first_player_ship,
                                                                 self.asteroids)
        second_player_collision = pygame.sprite.spritecollideany(self.second_player_ship,
                                                                  self.asteroids)

        if self.stats.player_one_active and first_player_collision:
            self._first_player_ship_hit()
            first_player_collision.kill()

        if self.stats.player_two_active and second_player_collision:
            self._second_player_ship_hit()
            second_player_collision.kill()


    def _shield_collisions(self, ships, aliens, bullets, asteroids):
        """Destroy any aliens that collide with the shield of any of the given ships."""
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


    def _first_ship_power_up(self):
        """Powers up the first player ship"""
        power_up_choice = random.randint(1, 5)
        if power_up_choice == 1:
            self.settings.first_player_ship_speed += 0.3
        elif power_up_choice == 2:
            self.settings.first_player_bullet_speed += 0.3
        elif power_up_choice == 3 and self.settings.thunder_bullet_count < 6:
            self.settings.thunder_bullet_count += 1
        elif power_up_choice == 4:
            self.first_player_ship.draw_shield()
        elif power_up_choice == 5:
            self.settings.first_player_bullets_allowed += 2


    def _second_ship_power_up(self):
        """Powers up the second player ship"""
        power_up_choice = random.randint(1, 5)
        if power_up_choice == 1 and self.settings.fire_bullet_count < 6:
            self.settings.fire_bullet_count += 1
        if power_up_choice == 2:
            self.settings.second_player_ship_speed += 0.3
            self.second_player_ship.draw_shield()
        elif power_up_choice == 3:
            self.settings.second_player_bullet_speed += 0.3
        elif power_up_choice == 4:
            self.second_player_ship.draw_shield()
        elif power_up_choice == 5:
            self.settings.second_player_bullets_allowed += 2


    def _first_health_power_up(self):
        """Increases the health of the first player"""
        if self.stats.ships_left < self.settings.max_ships:
            self.stats.ships_left += 1
            self.score_board.prep_hp()


    def _second_health_power_up(self):
        """Increases the health of the second player"""
        if self.stats.player_two_hp < self.settings.max_ships:
            self.stats.player_two_hp += 1
            self.score_board.prep_hp()


    def _check_alien_bullets_collisions(self):
        """Manages collisions between the alien bullets and the players"""
        first_player_collision = pygame.sprite.spritecollideany(self.first_player_ship,
                                                                 self.alien_bullet)
        second_player_collision = pygame.sprite.spritecollideany(self.second_player_ship,
                                                                  self.alien_bullet)

        if self.stats.player_one_active and first_player_collision:
            self._first_player_ship_hit()
            first_player_collision.kill()

        if self.stats.player_two_active and second_player_collision:
            self._second_player_ship_hit()
            second_player_collision.kill()


    def _first_player_ship_hit(self):
        """Respond to the first player ship being hit by an alien, bullet or asteroid."""
        if self.first_player_ship.exploding:
            return

        if self.stats.ships_left > 0:
            self.first_player_ship.explode()
            self.first_player_ship.shield_on = False
            self.settings.thunder_bullet_count = 1
            if self.settings.first_player_bullets_allowed > 1:
                self.settings.first_player_bullets_allowed -= 2
            self.stats.ships_left -= 1

            self.first_player_ship.center_ship()
            self.score_board.prep_hp()
        else:
            self.stats.player_one_active = False
            if self.stats.player_two_active:
                self.first_player_bullets.empty()
            else:
                self.stats.game_active = False


    def _second_player_ship_hit(self):
        """Respond to the second player ship being hit by an alien, bullet or asteroid."""
        if self.second_player_ship.exploding:
            return

        if self.stats.player_two_hp > 0:
            self.second_player_ship.explode()
            self.second_player_ship.shield_on = False
            self.settings.fire_bullet_count = 1
            if self.settings.second_player_bullets_allowed > 1:
                self.settings.second_player_bullets_allowed -= 2
            self.stats.player_two_hp -= 1

            self.second_player_ship.center_ship()
            self.score_board.prep_hp()
        else:
            self.stats.player_two_active = False
            if self.stats.player_one_active:
                self.second_player_bullets.empty()
            else:
                self.stats.game_active = False


    def _create_fleet(self):
        """Determine how many aliens fit on the screen and create the fleet of aliens."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (3 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.first_player_ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (12 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                # Randomly generate x and y coordinates for the alien.
                x_coord = random.randint(alien_width, available_space_x - alien_width)
                y_coord = random.randint(35, available_space_y - (2 * alien_height))

                # Create the alien and set its position.
                self._create_alien(alien_number, row_number)
                self.aliens.sprites()[-1].rect.x = x_coord + (alien_width * 1.5 * alien_number)
                self.aliens.sprites()[-1].rect.y = y_coord + (2 * alien_height * row_number)



    def _create_boss_alien(self):
        """Create a boss alien and add it to the aliens group."""
        boss_alien = BossAlien(self)
        self.aliens.add(boss_alien)


    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row"""
        alien = Alien(self)
        alien_width, _ = alien.rect.size
        alien.x_pos = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x_pos
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number + 45
        self.aliens.add(alien)


    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.first_player_ship, self.aliens):
            self._first_player_ship_hit()
        if pygame.sprite.spritecollideany(self.second_player_ship, self.aliens):
            self._second_player_ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()


    def _create_alien_bullet(self, alien):
        """Create an alien bullet at the specified alien rect"""
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
                    alien.rect.y += self.settings.fleet_drop_speed
                else:
                    alien.rect.x += (self.settings.alien_speed *
                                    alien.direction)


    def _check_aliens_bottom(self):
        """Check if an alien have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._first_player_ship_hit()
                self._second_player_ship_hit()
                break


    def _create_power_up(self):
        """Create a random power up"""
        if random.randint(0, 4) == 0:
            power_up = HealthPowerUp(self)
        else:
            power_up = PowerUp(self)
        power_up.rect.x = random.randint(0, self.settings.screen_width - power_up.rect.width)
        power_up.rect.y = random.randint(-100, -40)
        self.power_ups.add(power_up)


    def _check_game_over(self):
        """Check if the game is over and if so, display the game over image"""
        if not any([self.stats.game_active, self.stats.player_one_active,
                     self.stats.player_two_active]):
            self.screen.blit(self.game_over, self.game_over_rect)
            self.aliens.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()


    def _initialize_game_over(self):
        """Set the location of the game over image on the screen"""
        game_over_rect = self.game_over.get_rect()
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
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        quit_clicked = self.quit_button.rect.collidepoint(mouse_pos)
        menu_clicked = self.menu_button.rect.collidepoint(mouse_pos)
        difficulty_clicked = self.difficulty.rect.collidepoint(mouse_pos)
        easy_clicked = self.easy.rect.collidepoint(mouse_pos)
        medium_clicked = self.medium.rect.collidepoint(mouse_pos)
        hard_clicked = self.hard.rect.collidepoint(mouse_pos)

        if easy_clicked and not self.stats.game_active:
            self.settings.speedup_scale = 0.5
            self.show_difficulty = False
        if medium_clicked and not self.stats.game_active:
            self.settings.speedup_scale = 1.0
            self.show_difficulty = False
        if hard_clicked and not self.stats.game_active:
            self.settings.speedup_scale = 1.5
            self.show_difficulty = False
        if button_clicked and not self.stats.game_active:
            self.show_difficulty = False
            self._reset_game()
        if menu_clicked and not self.stats.game_active:
            self.run_menu()

        if difficulty_clicked and not self.stats.game_active:
            if self.show_difficulty:
                self.show_difficulty = False
            else:
                self.show_difficulty = True

        if quit_clicked and not self.stats.game_active:
            pygame.quit()
            sys.exit()


    def _reset_game(self):
        # Reset the game statistics.
        self.stats.reset_stats()
        self.second_stats.reset_stats()
        self.settings.initialize_dynamic_settings()
        self.stats.game_active = True
        self.score_board.prep_score()
        self.score_board.prep_level()
        self.score_board.prep_hp()

        # Get rid of remaining aliens, bullets, asteroids and power-ups.
        self.first_player_bullets.empty()
        self.second_player_bullets.empty()
        self.alien_bullet.empty()
        self.power_ups.empty()
        self.aliens.empty()
        self.asteroids.empty()

        # Create a new fleet, play the warp animation and center the ships.
        self.first_player_ship.start_warp()
        self.second_player_ship.start_warp()
        self.first_player_ship.center_ship()
        self.second_player_ship.center_ship()
        self._create_fleet()


    def _update_screen(self):
        """Update images on the screen"""
        if self.stats.player_one_active and self.stats.game_active:
            self.first_player_ship.blitme()
            for bullet in self.first_player_bullets.sprites():
                bullet.draw_bullet()

        if self.stats.player_two_active and self.stats.game_active:
            self.second_player_ship.blitme()
            for bullet in self.second_player_bullets.sprites():
                bullet.draw_bullet()

        if self.stats.game_active:
            for bullet in self.alien_bullet.sprites():
                bullet.draw_bullet()

            for power_up in self.power_ups.sprites():
                power_up.draw_powerup()

            for asteroid in self.asteroids.sprites():
                asteroid.draw_asteroid()


            self.aliens.draw(self.screen)
            self.score_board.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()
            self.quit_button.draw_button()
            self.menu_button.draw_button()
            self.difficulty.draw_button()

            if self.show_difficulty:
                self.easy.draw_button()
                self.medium.draw_button()
                self.hard.draw_button()

        pygame.display.flip()



class SingleplayerAlienOnslaught(AlienOnslaught):
    """A class that manages the Singleplayer version of the game"""
    def __init__(self):
        super().__init__()
        self.score_board = SecondScoreBoard(self)
        self.clock = pygame.time.Clock()
        self.first_player_ship = Thunderbird(self, 602, 612)
        self.first_player_ship.single_player = True
        self.ships = [self.first_player_ship]
        self.show_difficulty = False

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
                    self._handle_level_tasks()
                    self._create_power_ups()
                    self._update_power_ups()
                    self._update_alien_bullets()
                    self._check_alien_bullets_collisions()
                    self._check_power_ups_collisions()
                    self._update_bullets()
                    self._update_aliens()
                    self.first_player_ship.update_state()
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
                        self.first_player_ship.moving_right = True
                    case pygame.K_LEFT:
                        self.first_player_ship.moving_left = True
                    case pygame.K_UP:
                        self.first_player_ship.moving_up = True
                    case pygame.K_DOWN:
                        self.first_player_ship.moving_down = True
                    case pygame.K_RETURN:
                        self._fire_bullet(
                            self.first_player_bullets,
                            self.settings.first_player_bullets_allowed,
                            bullet_class=Thunderbolt,
                            num_bullets=self.settings.thunder_bullet_count,
                            ship=self.first_player_ship)
                        self.fire_sound.play()
                    case pygame.K_KP1:
                        self.first_player_ship.image = self.first_player_ship.ship_images[0]
                    case pygame.K_KP2:
                        self.first_player_ship.image = self.first_player_ship.ship_images[1]
                    case pygame.K_KP3:
                        self.first_player_ship.image = self.first_player_ship.ship_images[2]


    def _check_keyup_events(self, event):
        """Respot to key releases."""
        match event.key:
            case pygame.K_RIGHT:
                self.first_player_ship.moving_right = False
            case pygame.K_LEFT:
                self.first_player_ship.moving_left = False
            case pygame.K_UP:
                self.first_player_ship.moving_up = False
            case pygame.K_DOWN:
                self.first_player_ship.moving_down = False


    def _reset_game(self):
        # Reset the game statistics.
        self.stats.reset_stats()
        self.settings.initialize_dynamic_settings()
        self.stats.game_active = True
        self.score_board.prep_score()
        self.score_board.prep_level()
        self.score_board.prep_hp()

        # Get rid of the remaining aliens, bullets, asteroids and power ups
        self.first_player_bullets.empty()
        self.alien_bullet.empty()
        self.power_ups.empty()
        self.aliens.empty()
        self.asteroids.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.first_player_ship.start_warp()
        self.first_player_ship.center_ship()


    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.first_player_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.first_player_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.first_player_bullets.remove(bullet)
        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        first_player_ship_collisions = pygame.sprite.groupcollide(
            self.first_player_bullets, self.aliens, True, False)

        if first_player_ship_collisions:
            for aliens in first_player_ship_collisions.values():
                for alien in aliens:
                    alien.hit_count += 1
                    if isinstance(alien, BossAlien):
                        if alien.hit_count >= self.settings.boss_hp:
                            self.aliens.remove(alien)
                            self.stats.score += self.settings.boss_points
                            self.score_board.prep_score()
                            self.score_board.check_high_score()
                    else:
                        if self.stats.level < 5:
                            if alien.hit_count >= 1:
                                self._update_stats(alien, 'player_1')
                        elif self.stats.level < 10:
                            if alien.hit_count >= 2:
                                self._update_stats(alien, 'player_1')
                        else:
                            if alien.hit_count >= 3:
                                self._update_stats(alien, 'player_1')

        if not self.aliens:
            self._handle_alien_creation()
            self.power_ups.empty()
            self.alien_bullet.empty()
            self.asteroids.empty()
            self.first_player_bullets.empty()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.score_board.prep_level()

    def _check_power_ups_collisions(self):
        """Check for collision between a ship and a power-up"""
        collision = pygame.sprite.spritecollideany(self.first_player_ship, self.power_ups)

        if self.stats.player_one_active and collision:
            if isinstance(collision, PowerUp):
                self._first_ship_power_up()
            elif isinstance(collision, HealthPowerUp):
                self._first_health_power_up()
            collision.kill()


    def _check_asteroids_collisions(self):
        """Check for collisions between the ship and asteroids"""
        collision = pygame.sprite.spritecollideany(self.first_player_ship, self.asteroids)

        if self.stats.player_one_active and collision:
            self._first_player_ship_hit()
            collision.kill()


    def _first_player_ship_hit(self):
        """Respond to the first player ship being hit by an alien."""
        if self.first_player_ship.exploding:
            return

        if self.stats.ships_left > 0:
            self.first_player_ship.explode()
            self.first_player_ship.shield_on = False
            self.settings.thunder_bullet_count = 1
            if self.settings.first_player_bullets_allowed > 1:
                self.settings.first_player_bullets_allowed -= 2
            self.stats.ships_left -= 1
            self.first_player_ship.center_ship()
            self.score_board.prep_hp()
        else:
            self.stats.player_one_active = False
            self.stats.game_active = False

    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.first_player_ship, self.aliens):
            self._first_player_ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()


    def _check_game_over(self):
        if not self.stats.game_active and not self.stats.player_one_active:
            self.screen.blit(self.game_over, self.game_over_rect)
            self.aliens.empty()
            self.power_ups.empty()
            self.alien_bullet.empty()


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        if self.stats.player_one_active and self.stats.game_active:
            self.first_player_ship.blitme()

            for bullet in self.first_player_bullets.sprites():
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
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.quit_button.draw_button()
            self.menu_button.draw_button()
            self.difficulty.draw_button()

            if self.show_difficulty:
                self.easy.draw_button()
                self.medium.draw_button()
                self.hard.draw_button()

        pygame.display.flip()


if __name__ =='__main__':
    start = AlienOnslaught()
    start.run_menu()
