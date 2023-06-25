"""
This module tests miscellaneous functions that are used
 throughout the other modules in the game.
 """

import unittest
from unittest.mock import patch, MagicMock, call

import pygame

from src.utils.game_utils import (
    get_colliding_sprites,
    get_boss_rush_title,
    display_game_modes_description,
    render_bullet_num,
    display_message,
    display_laser_message,
    render_text,
)


class MiscFunctionsTests(unittest.TestCase):
    """Test miscellaneous functions."""

    @patch("pygame.sprite.spritecollide")
    def test_get_colliding_sprites(self, mock_spritecollide):
        """Test the get_colliding_sprites function."""
        ship = MagicMock()
        bullets_or_missiles = MagicMock()
        mock_spritecollide.return_value = ["sprite1", "sprite2"]

        result = get_colliding_sprites(ship, bullets_or_missiles)

        # Assert the return value and that spritecollide was called with the correct arguments
        self.assertEqual(result, ["sprite1", "sprite2"])
        mock_spritecollide.assert_called_once_with(ship, bullets_or_missiles, False)

    @patch("src.utils.game_utils.BOSS_RUSH")
    def test_get_boss_rush_title(self, mock_boss_rush):
        """Test the get_boss_rush_title function."""
        level = 2
        mock_boss_rush.get.return_value = "boss2"

        result = get_boss_rush_title(level)

        # Assert the return value and that BOSS_RUSH.get was called with the correct arguments
        self.assertEqual(result, "Boss2")
        mock_boss_rush.get.assert_called_once_with("boss2", "Level 2")

    @patch("pygame.font.SysFont")
    @patch("src.utils.game_utils.render_text")
    def test_display_game_modes_description(self, mock_render_text, mock_sysfont):
        """Test the display_game_modes_description function."""
        screen = MagicMock(spec=pygame.Surface)
        screen.get_size.return_value = (100, 200)
        description = "Game modes description"

        # Mock the necessary objects and functions
        font = MagicMock()
        text_surfaces = ["surface1", "surface2"]
        text_rects = ["rect1", "rect2"]
        mock_sysfont.return_value = font
        mock_render_text.return_value = (text_surfaces, text_rects)

        display_game_modes_description(screen, description)

        # Assert that the necessary objects and functions were called with the correct arguments
        screen_width, screen_height = screen.get_size()
        mock_sysfont.assert_called_once_with("verdana", 15)
        mock_render_text.assert_called_once_with(
            description,
            font,
            "white",
            (screen_width // 2 + 74, screen_height // 2 + 120),
            int(screen_height * 0.03),
        )
        for i, surface in enumerate(text_surfaces):
            screen.blit.assert_any_call(surface, text_rects[i])

    @patch("pygame.font.SysFont")
    def test_render_bullet_num(self, mock_sysfont):
        """Test the render_bullet_num function."""
        bullets = 10
        x_pos = 100
        y_pos = 200

        # Mock the necessary objects and functions
        font = MagicMock()
        font.render.return_value = MagicMock()
        mock_sysfont.return_value = font

        # Case for the right_aligned=False
        bullets_num_img, bullets_num_rect = render_bullet_num(bullets, x_pos, y_pos)

        # Assert the returned image and rect
        self.assertEqual(bullets_num_img, font.render.return_value)
        self.assertEqual(bullets_num_rect, bullets_num_img.get_rect.return_value)
        self.assertEqual(bullets_num_rect.top, y_pos)
        self.assertEqual(bullets_num_rect.left, x_pos)
        font.render.assert_called_once_with(
            f"Remaining bullets: {bullets}", True, (238, 75, 43), None
        )
        bullets_num_img.get_rect.assert_called_once()

        font.render.reset_mock()
        bullets_num_img.get_rect.reset_mock()

        # Case for the right_aligned=True
        bullets_num_img, bullets_num_rect = render_bullet_num(
            bullets, x_pos, y_pos, right_aligned=True
        )

        # Assert the returned image and rect
        self.assertEqual(bullets_num_img, font.render.return_value)
        self.assertEqual(bullets_num_rect, bullets_num_img.get_rect.return_value)
        self.assertEqual(bullets_num_rect.top, y_pos)
        self.assertEqual(bullets_num_rect.right, x_pos)
        font.render.assert_called_once_with(
            f"Remaining bullets: {bullets}", True, (238, 75, 43), None
        )
        bullets_num_img.get_rect.assert_called_once()

    def test_display_message(self):
        """Test the display_message function."""
        screen = MagicMock(spec=pygame.Surface)
        screen.get_width.return_value = 800
        screen.get_height.return_value = 600

        message = "Test Message"
        duration = 2.5

        font_mock = MagicMock(spec=pygame.font.Font)
        render_mock = font_mock.render
        get_rect_mock = render_mock.return_value.get_rect
        expected_rect = get_rect_mock.return_value

        with patch("pygame.font.SysFont", return_value=font_mock), patch(
            "pygame.display.flip"
        ), patch("pygame.time.wait") as time_wait_mock:
            display_message(screen, message, duration)

            # Assert that the necessary objects and functions were called with the correct arguments
            pygame.font.SysFont.assert_called_once_with("verdana", 14)
            render_mock.assert_called_once_with(message, True, (255, 255, 255))

            rect_args, _ = screen.blit.call_args
            self.assertEqual(rect_args[0], render_mock.return_value)
            self.assertEqual(rect_args[1], expected_rect)

            pygame.display.flip.assert_called_once()
            time_wait_mock.assert_called_once_with(int(duration * 1000))

    @patch("pygame.font.SysFont")
    def test_display_laser_message(self, mock_sysfont):
        """Test the display_laser_message function."""
        screen = MagicMock()
        message = "Laser message"
        ship = MagicMock()

        # Mock the necessary objects and functions
        font = MagicMock()
        text_surface = MagicMock()
        text_rect = MagicMock()
        mock_sysfont.return_value = font
        font.render.return_value = text_surface
        text_surface.get_rect.return_value = text_rect

        # Test the functionality with the cosmic=False
        display_laser_message(screen, message, ship, cosmic=False)

        # Assert that the necessary objects and functions were called with the correct arguments
        mock_sysfont.assert_called_once_with("verdana", 10)
        font.render.assert_called_once_with(message, True, (255, 0, 0))
        ship_rect = ship.rect
        text_surface.get_rect.assert_called_once_with(
            center=(ship_rect.right + 18, ship_rect.centery - 30)
        )
        screen.blit.assert_called_once_with(text_surface, text_rect)

        # Test the functionality with the cosmic=True
        text_surface.reset_mock()
        display_laser_message(screen, message, ship, cosmic=True)
        text_surface.get_rect.assert_called_once_with(
            center=(ship_rect.left + 18, ship_rect.centery - 35)
        )

    def test_render_text(self):
        """Test the render_text function."""
        text = "Text\nwith\nnew lines\tand\ttabs"
        font = MagicMock()
        color = "white"
        start_pos = (100, 200)
        line_spacing = 30

        render_mock = font.render
        render_mock.return_value = MagicMock(spec=pygame.Surface)

        result_text_surfaces, result_text_rects = render_text(
            text, font, color, start_pos, line_spacing
        )

        # Assert the returned text surfaces and rects
        expected_lines = (
            text.count("\n") + 1
        )  # Count the number of lines in the input text
        self.assertEqual(len(result_text_surfaces), expected_lines)
        self.assertEqual(len(result_text_rects), expected_lines)
        self.assertEqual(
            result_text_surfaces, [render_mock.return_value] * expected_lines
        )
        self.assertEqual(
            result_text_rects,
            [render_mock.return_value.get_rect.return_value] * expected_lines,
        )

        # Prepare the expected render calls
        expected_calls = []
        lines = text.split("\n")
        for line in lines:
            # Replace tabs with spaces in the expected line
            expected_line = line.replace("\t", " " * 10)
            expected_calls.append(call(expected_line, True, color, None))

        # Check the render calls
        render_mock.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(
            render_mock.call_count, expected_lines
        )  # Check the number of render calls

        expected_get_rect_calls = [
            call(topleft=(100, 200 + i * line_spacing))
            for i in range(expected_lines)
        ]
        # Check the get_rect calls
        render_mock.return_value.get_rect.assert_has_calls(
            expected_get_rect_calls, any_order=True
        )
        self.assertEqual(
            render_mock.return_value.get_rect.call_count, expected_lines
        )  # Check the number of get_rect calls


if __name__ == "__main__":
    unittest.main()