import pygame as pg
import pygame.mixer


class Sound:
    def __init__(self):
        pg.mixer.init()
        # Load sounds
        self.bg_music = pg.mixer.Sound('Background.mp3')
        self.explosion_sound = pg.mixer.Sound('Explode.mp3')
        self.ballin_sound = pg.mixer.Sound('ballin.mp3')
        self.levelwin = pg.mixer.Sound('levelwin.mp3')
        # Create channels
        self.bg_channel = pg.mixer.Channel(0)  # For background music
        self.effect_channel = pg.mixer.Channel(1)  # For sound effects
        self.effect2_channel = pg.mixer.Channel(2)
        self.effect3_channel = pg.mixer.Channel(3)

    def play_background_music(self):
        self.bg_channel.play(self.bg_music, loops=-1)  # Loop indefinitely

    def stop_background_music(self):
        self.bg_channel.stop()

    def play_bucket_explosion(self):
        self.effect_channel.play(self.explosion_sound)
    
    def play_bucket_in_sound(self):
        self.effect2_channel.play(self.ballin_sound)

    def play_level_win_sound(self):
        self.effect3_channel.play(self.levelwin)