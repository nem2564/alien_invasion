class Settings:
    """A class to store all the game settings."""
    def __init__(self):
        """Constructore : Initialize the game settings."""
        
        #Screen settings.
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230,230,230)

        # Ship seettings.
        self.ship_speed = 1.5 # Ship moves 1.5 pixel per one while loop.
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed = 1.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Alien settings
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # Fleet direction of 1 represents right and -1 represents left
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50
