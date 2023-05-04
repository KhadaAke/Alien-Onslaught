"""The "utils" module provides various utility functions"""
import sys
import os
import json
import pygame

from .constants import (
    P1_CONTROLS, P2_CONTROLS,
    BOSS_RUSH, ALIEN_BULLETS_IMG,
)


def load_images(image_dict):
    """A function that loads multiple images from a dict of the form:
    key: image name 
    value: path to image location"""
    return {key: pygame.image.load(value) for key, value in image_dict.items()}

def load_sound_files(sounds_dict):
    """A function that loads multiple sounds from a dict of the form:
    key: sound name:
    value: path to sound location."""
    pygame.mixer.init()
    return {key: pygame.mixer.Sound(value) for key, value in sounds_dict.items()}

def set_sounds_volume(sounds, volume):
    """Set the volume for all sounds in the passed sounds dict."""
    for sound in sounds.values():
        sound.set_volume(volume)

def play_sound(sounds_list, sound_name, loop=False):
    """Plays a certain sound located in the 'sounds_list'."""
    if loop:
        sounds_list[sound_name].play(-1)
    else:
        sounds_list[sound_name].play()

def load_frames(filename_pattern, num_frames, frame_list, start=0):
    """Loads a sequence of images frames into a list"""
    for i in range(start, start + num_frames):
        filename = filename_pattern.format(i)
        path = os.path.join("images", filename)
        image = pygame.image.load(path)
        frame_list.append(image)


def load_alien_images(alien_prefix):
    """Load the images for the given alien prefix."""
    frames = []
    for i in range(6):
        filename = f'images/aliens/{alien_prefix}_{i}.png'
        frame = pygame.image.load(filename)
        frames.append(frame)

    return frames

def resize_image(image, screen_size=None):
    """Resizes an image to match the current screen size."""
    if screen_size is None:
        screen_size = pygame.display.get_surface().get_size()
    return pygame.transform.smoothscale(image, screen_size)


def load_button_imgs(button_names):
    """Load button images"""
    button_images = {}
    for name in button_names:
        filename = f"images/buttons/{name}.png"
        button_images[name] = filename
    return button_images


def load_controls_image(image_loc, image_name, position):
    """Loads images for controls displayed on menu screen"""
    image = pygame.image.load(image_loc[image_name])
    rect = image.get_rect(**position)
    return image, rect


def load_boss_images():
    """Loads and returns a dict of boss images"""
    return {
        alien_name: pygame.image.load(alien_image_path)
        for alien_name, alien_image_path in BOSS_RUSH.items()
    }


def load_alien_bullets():
    """Loads and returns a dict of alien bullet images."""
    return {
        bullet_name: pygame.image.load(bullet_image_path)
        for bullet_name, bullet_image_path in ALIEN_BULLETS_IMG.items()
    }


def render_text(text, font, color, start_pos, line_spacing, second_color=None):
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


def display_high_scores(game, screen, score_key):
    """Display the high scores on the screen."""
    # Load the high score data from the JSON file,
    # or create a new high score list if there is an error
    filename = 'single_high_score.json' if game.singleplayer else 'high_score.json'
    try:
        with open(filename, 'r', encoding='utf-8') as score_file:
            high_scores = json.load(score_file)
    except json.JSONDecodeError:
        high_scores = {'high_scores': [0] * 10}

    # Get the scores from the high score list and create a new list of tuples
    # containing the score and its rank
    try:
        scores = high_scores[score_key]
    except KeyError:
        scores = []

    ranked_scores = [
        (i+1, entry['name'], entry['score'])
        for i, entry in enumerate(scores)
        if isinstance(entry, dict)
    ]


    rank_strings = [
        f"{('1st' if rank == 1 else '2nd' if rank == 2 else '3rd' if rank == 3 else rank)} {name}" 
        for rank, name, score in ranked_scores
    ]
    score_strings = [f"{score}" for rank, name, score in ranked_scores]

    score_text = "\n".join(score_strings)
    rank_text = "\n".join(rank_strings)

    # Calculate the relative position of the text based on the screen size
    screen_width, screen_height = screen.get_size()
    centerx = int(screen_width / 2)
    centery = int(screen_height / 2)
    title_x = int(centerx - 520)
    title_y = int(centery - 150)
    rank_x = int(centerx - 550)
    rank_y = int(centery - 50)
    score_x = int(centerx - 270)
    score_y = rank_y

    # Render the score text and rank text as surfaces with new lines using different fonts
    font = pygame.font.SysFont('impact', int(screen_height * 0.07))
    text_surfaces, text_rects = render_text(
            "HIGH SCORES",
            font,
            (255, 215, 0),
            (title_x, title_y),
            int(screen_height * 0.06))

    font = pygame.font.SysFont('impact', int(screen_height * 0.05))
    rank_surfaces, rank_rects = render_text(
            rank_text,
            font,
            'red',
            (rank_x, rank_y),
            int(screen_height * 0.05))

    font = pygame.font.SysFont('impact', int(screen_height * 0.05))
    scores_surfaces, scores_rects = render_text(
            score_text,
            font,
            'red',
            (score_x, score_y),
            int(screen_height * 0.05))

    # Blit the score text surfaces onto the screen using a loop to avoid repetitive code
    for surfaces, rects in [(text_surfaces, text_rects), (rank_surfaces, rank_rects),
                                    (scores_surfaces, scores_rects)]:
        for surface, rect in zip(surfaces, rects):
            screen.blit(surface, rect)


def display_game_modes_description(screen, description):
    """Render game modes description on screen."""
    screen_width, screen_height = screen.get_size()
    font = pygame.font.SysFont('verdana', int(screen_height * 0.021))
    text_x = int(screen_width * 0.56)
    text_y = 430
    text_surfaces, text_rects = render_text(
                        description,
                        font,
                        'white',
                        (text_x, text_y),
                        int(screen_height * 0.03))

    for i, surface in enumerate(text_surfaces):
        screen.blit(surface, text_rects[i])


def display_controls(buttons, settings):
    """Display controls on screen"""
    p1_controls, p1_controls_rect = load_controls_image(
                                            buttons,
                                            'player_controls',
                                            {'topleft': (50, 220)})
    p2_controls, p2_controls_rect = load_controls_image(
                                            buttons,
                                            'player_controls',
                                            {'topright':
                                            (settings.get_width() - 50, 220)})

    font = pygame.font.SysFont('arialbold', 35)
    color = 'white'
    t1_surfaces, t1_rects = render_text(
                                P1_CONTROLS,
                                font, color,
                                (p1_controls_rect.left + 30,
                                p1_controls_rect.top + 30), 25)
    t2_surfaces, t2_rects = render_text(
                                    P2_CONTROLS,
                                    font, color,
                                    (p2_controls_rect.left + 30,
                                    p2_controls_rect.top + 30), 25)

    return (p1_controls, p1_controls_rect,
            p2_controls, p2_controls_rect,
            t1_surfaces, t1_rects,
            t2_surfaces, t2_rects)

def display_message(screen, message, duration):
    """Display a message on the screen for a specified amount of time."""
    font = pygame.font.SysFont('verdana', 14)
    text = font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 25))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(int(duration * 1000))


def get_player_name(screen, background_image, game_over_img=None, game_over_rect=None):
    """Get the player name for the high score."""

    # Set up fonts and colors
    font = pygame.font.SysFont('verdana', 19)
    text_font = pygame.font.SysFont('verdana', 23)
    text_color = pygame.Color('silver')

    # Set up input box and initial player name
    input_box = pygame.Rect(0, 0, 200, 26)
    input_box.center = (screen.get_width() / 2 + 100, screen.get_height() / 2)
    player_name = 'Player'

    # Loop until player name is confirmed
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return player_name  # exit loop and return player name
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.unicode.isalnum():
                    player_name += event.unicode
                    player_name = player_name[:12]  # limit length of player name to 12 characters

        # Draw the input box and player name
        screen.blit(background_image, (0, 0))
        if game_over_img is not None and game_over_rect is not None:
            screen.blit(game_over_img, game_over_rect)
        pygame.draw.rect(screen, text_color, input_box, 1)
        text_surface = font.render(player_name, True, pygame.Color(90, 90, 90))
        screen.blit(text_surface, (input_box.x + 5, input_box.y))

        # Draw the text label
        text_surface = text_font.render("High score name:", True, text_color)
        text_x = input_box.centerx - text_surface.get_width() / 2 - 205
        text_y = input_box.centery - 18
        screen.blit(text_surface, (text_x, text_y))

        pygame.display.flip()

