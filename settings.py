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

