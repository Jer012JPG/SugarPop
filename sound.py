import pygame as pg
import pygame.mixer


class Sound :
    def __init__(self):
        pg.init()
        pygame.mixer.init()
        # Load BG Sound
        pg.mixer.music.load('Background.mp3')
        
        # Load Explotion and Bucket Sound
        self.explotion_sound = pg.mixer.Sound('Explode.mp3')
        #self.Bucket_in_sound = pg.mixer.Sound("belom nemu")

        # Create sound channel
        #self.channel_ball = pygame.mixer.Channel(1)
        #self.channel_explosion = pygame.mixer.Channel(2)



    def play_background_music(self, loop=True):
        pygame.mixer.music.play()

    def stop_background_music(self):
        pygame.mixer.music.stop()

    def play_ball_in_bucket(self):
        self.channel_ball.play(self.Bucket_in_sound)

    def play_bucket_explosion(self):
        self.explotion_sound.play()
    