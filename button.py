"""
Button module
This module contains the class that creates instances of buttons for the game
"""
import pygame.font
import pygame

class Button:
    """A class that manages the button"""
    def __init__(self, ai_game, image_loc, pos, center=False):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Load button image and scale it to the desired size.
        self.image = pygame.image.load(image_loc)

        # Build the button's rect object and set its position.
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

        if center:
            self.rect.center = self.screen_rect.center
        else:
            self.rect.x, self.rect.y = pos

    def update_pos(self, *args):
        """Update the button's position."""
        if len(args) == 1:
            self.rect.center = args[0]
        elif len(args) == 2:
            self.rect.topleft = args

    def draw_button(self):
        """Draws the button"""
        self.screen.blit(self.image, self.rect)
