import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create game resources."""
        pygame.init()

        # Create Settings object or instance
        self.settings = Settings()
        # Run game in full-screen mode.
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        # Run game in 1200 X 800 window.
        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        # No need to set here after creating settings class.
        # self.screen = pygame.display.set_mode((1200,800))

        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics.
        self.stats = GameStats(self)
        # Create a scoreboard
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game"""
        while True:
            # Calling helper function for events.
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._udpate_bullets()
                self._udpate_aliens()

            # Calling helper function for screen update.
            self._update_screen()      
    
    def _check_events(self):
        """responds to keypresses and mouse events."""
        # Watch for the keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:      # Check event type. i.e. keydown event
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                   
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:     # Check if key pressed is right aero key
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        # Press q to Quit the game
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullet group. i.e. at line 31"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _udpate_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            # print(len(self.bullets))
        
        self._check_bullet_alien_collision()

    def _check_bullet_alien_collision(self):
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        # This true of one bullet one alien but in reality bigger bullet can hit multiple aliens.
        # OR two bullet can collid with aliens during the same pass through loop.
        # # For single bullet implementation.
        # if collisions:
        #     self.stats.score += self.settings.alien_points
        #     self.sb.prep_score()

        # For all the cases to be covered
        if collisions:
            for alines in collisions.values():
                self.stats.score += self.settings.alien_points * len(alines)
            self.sb.prep_score()


        if not self.aliens:
            # No aliens left in the fleet, recreate the fleet and destroy existing bullets.
            self.bullets.empty()
            self._create_fleet() 

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        # Update bullet location
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screeen visible.
        pygame.display.flip()

    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Create an alien and find the number of aliens in a row.
        # spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x//(2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens
        for row_number in range(number_rows):
            # Create the one row of aliens.
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
            
    def _create_alien(self, alien_number, row_number):
        # Create an alien and place in the row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _udpate_aliens(self):
        """
        Check if the fleet is at the edge then
        Update the position of all the aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for any alien to hit the bottom screen.
        self._check_aliens_bottom()
    
    def _check_fleet_edges(self):
        """Respond appropriently if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the etire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by alien."""

        if self.stats.ships_left > 0:
            # Decrement ship left.
            self.stats.ships_left -= 1

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            # Mouse cursor needs to reappear after game ends
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same same as ship got hit.
                self._ship_hit()
                break

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.game_active = True
            # Reset the game stats and scoreboard.
            self.stats.reset_stats()
            self.sb.prep_score()

            # Get rid of any aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

if __name__ == '__main__':
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()