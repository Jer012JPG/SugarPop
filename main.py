#############################################################
# Module Name: Sugar Pop Main Module
# Project: Sugar Pop Program
# Date: Nov 17, 2024
# By: Brett W. Huffman
# Description: The main implementation of the sugar pop game
#############################################################

import pygame as pg
import pymunk  # Import Pymunk library
import sys
from settings import *
import random
import static_item
import dynamic_item
import sugar_grain
import bucket
import level
import message_display
import sound

from bucket import Bucket


class Game:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.iter = 0
        
        # Initialize font for HUD
        self.font = pg.font.SysFont(None, 36)  # Default font, size 36

        # Create a Pymunk space with gravity
        self.current_level = 3
        self.tornado_active = False
        # Create sound
        self.sound = sound.Sound()
        self.action_active = False
        # Make current position of spout
        self.current_spout = 0
        self.level_complete = False
        self.space = pymunk.Space()
        self.space.gravity = (0, -9.8)  # Gravity pointing downwards in Pymunk's coordinate system
        # Iterations defaults to 10. Higher is more accurate collison detection
        self.space.iterations = 30 
        self.is_paused = False
        self.drawing_lines = []
        self.sugar_grains = []
        self.buckets = []
        self.statics = []
        self.total_sugar_count = None
        self.level_spout_position = None
        self.level_grain_dropping = None
        self.mouse_down = False
        self.current_line = None
        self.message_display = message_display.MessageDisplay(font_size=72)
        
        # Load the intro image
        self.intro_image = pg.image.load("./images/SugarPop.png").convert()  # Load the intro image
        # Get new height based on correct scale
        scale_height = self.intro_image.get_height() * WIDTH / self.intro_image.get_width()
        self.intro_image = pg.transform.scale(self.intro_image, (WIDTH, int(scale_height)))  # Scale to screen resolution
        self.sound.play_background_music()
        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)  # Load in 2 seconds
        

    def load_level(self, levelnumber=0):
        # Destroy any current game objects
        for item in self.sugar_grains:
            item.delete()  # Delete all sugar grains
        for item in self.drawing_lines:
            item.delete() 
        for item in self.buckets:
            item.delete() 
        for item in self.statics:
            item.delete() 
        
        self.sugar_grains = []
        self.drawing_lines = []  # Clear the list
        self.buckets = []
        self.statics = []
      
 
        new_level = LEVEL_FILE_NAME.replace("X", str(levelnumber))
        self.level = level.Level(new_level)
        
        # Make sure the file was found
        if not self.level or not self.level.data:
            return False
        else:  # Do final steps to start the level
            self.level_grain_dropping = False
            self.level_spout_position = (self.level.data['spout_x'], self.level.data['spout_y'])
            self.build_main_walls()

            # Load buckets
            for nb in self.level.data['buckets']:
                self.buckets.append(bucket.Bucket(self.space, nb['x'], nb['y'], nb['width'], nb['height'], nb['needed_sugar']))
            # Load static buckets
            
            # Load static items
            for nb in self.level.data['statics']:
                self.statics.append(static_item.StaticItem(self.space, nb['x1'], nb['y1'], nb['x2'], nb['y2'], nb['color'], nb['line_width'], nb['friction'], nb['restitution']))
            self.total_sugar_count = self.level.data['number_sugar_grains']
            pg.time.set_timer(START_FLOW, 5 * 1000)  # 5 seconds
            self.message_display.show_message("Level Up", 10)
            self.level_complete = False
            #self.sound
            return True

    def build_main_walls(self):
        '''Build the walls, ceiling, and floor of the screen'''
        # Floor
        floor = static_item.StaticItem(self.space, 0, 0, WIDTH, 0, 'red', 5)
        self.statics.append(floor)
        # Left Wall
        left_wall = static_item.StaticItem(self.space, 0, 0, 0, HEIGHT, 'red')
        self.statics.append(left_wall)
        # Right Wall
        right_wall = static_item.StaticItem(self.space, WIDTH, 0, WIDTH, HEIGHT, 'red')
        self.statics.append(right_wall)
        # Ceiling
        ceiling = static_item.StaticItem(self.space, 0, HEIGHT, WIDTH, HEIGHT, 'red')
        self.statics.append(ceiling)
    
    def check_all_buckets_exploded(self):
        """
        Check if all buckets have exploded.
        """
        return all(bucket.exploded for bucket in self.buckets)

    def update(self):
        '''Update the program physics'''

        if self.is_paused:
            return
        
        # Keep an overall iterator
        self.iter += 1
        
        # Calculate time since last frame
        delta_time = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        # Cap delta_time to prevent instability from large time steps
        time_step = min(delta_time, MAX_TIME_STEP)

        # Step the physics simulation forward with the calculated time_step
        self.space.step(time_step)
        
        # Update our game counter
        if self.iter == 60:
            self.iter = 0

        pg.display.set_caption(f'fps: {self.clock.get_fps():.1f}')
        
        # Only do the following every 20 frames for less system stress
        if self.iter % 20 == 0:
            # Update any messages
            self.message_display.update()
            
            # Calculate buckets count by counting each grain's position
            # First, explode or reset the counter on each bucket
            for i in range(len(self.buckets)-1, -1, -1):
               bucket = self.buckets[i]
               if bucket.count >= bucket.needed_sugar:
                   bucket.explode(self.sugar_grains)
                   self.sound.play_bucket_explosion()
                   del self.buckets[i]
                   del self.level.data['buckets'][i] 
                    # If all the buckets are gone, level up!
                   if not self.level_complete and self.check_all_buckets_exploded():
                        self.sound.play_level_win_sound()
                        self.level_complete = True
                        
                        self.message_display.show_message("Level Complete!", 2)
                        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)  # Schedule next level load
                   else:
                    bucket.count_reset()
            # Count the grains in the un-exploded buckets
            for grain in self.sugar_grains:
                for bucket in self.buckets:
                    bucket.collect(grain)

                
            if self.level_grain_dropping:
                # Create new sugar to drop
                new_sugar = sugar_grain.sugar_grain(self.space, self.level_spout_position[0], self.level_spout_position[1], 0.1)
                self.sugar_grains.append(new_sugar)
                # Check if it's time to stop
                if len(self.sugar_grains) >= self.total_sugar_count:
                    self.level_grain_dropping = False
         
            
    def draw_hud(self):
        """Draw the HUD displaying the number of grains."""
        if self.total_sugar_count is not None:
            # Render the current level text
            level_surface = self.font.render(f'Level {self.current_level}', True, (255, 255, 255))
            self.screen.blit(level_surface, (10, 10))

            # Render the remaining sugar grains text
            remaining_grains = self.total_sugar_count - len(self.sugar_grains)
            sugar_surface = self.font.render(f'Sugar Left: {remaining_grains}', True, (255, 255, 255))
            self.screen.blit(sugar_surface, (10, 50))

            # Display the count for each remaining bucket
            for bucket, bucket_data in zip(self.buckets, self.level.data['buckets']):
                bucket_status = self.font.render(f'{bucket.count}/{bucket.needed_sugar}', True, (255, 255, 255))
                self.screen.blit(bucket_status, (bucket_data['x'] - 20, HEIGHT - bucket_data['y'] - 30))
        
            

    def draw(self):
        '''Draw the overall game. Should call individual item draw() methods'''
        # Clear the screen
        self.screen.fill('black')

        # Only show the intro screen if we haven't loaded a level yet
        if self.intro_image:
            self.screen.blit(self.intro_image, (0, 0))  # Draw the intro image
    
        for bucket in self.buckets:
            bucket.draw(self.screen)

        # Draw each sugar grain
        for grain in self.sugar_grains:
            grain.draw(self.screen)

        # Draw the current dynamic line
        if self.current_line is not None:
            self.current_line.draw(self.screen)
        
        # Draw the user-drawn lines
        for line in self.drawing_lines:
            line.draw(self.screen)
            
        # Draw any static items
        for static in self.statics:
            static.draw(self.screen)

          # Draw the nozzle (Remember to subtract y from the height)
        if self.level_spout_position:
            pg.draw.line(
                self.screen, 
                (255, 165, 144), 
                (self.level_spout_position[0], HEIGHT - self.level_spout_position[1] - 10), 
                (self.level_spout_position[0], HEIGHT - self.level_spout_position[1]), 
                5
            )
        # Draw the heads-up display
        self.draw_hud()

        # Show any messages needed        
        self.message_display.draw(self.screen)

        # Update the display
        pg.display.update()

    def check_events(self):
        '''Check for keyboard and mouse events'''
        for event in pg.event.get():
            if event.type == EXIT_APP or event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            # IMPLEMENTING NORMAL GRAVITY
            elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
                self.space.gravity = (0, 9.8)
                self.message_display.show_message("REVERSE GRAVITY!", 1)
            # IMPLEMENTING REVERSE GRAVITY
            elif event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                self.space.gravity = (0,-9.8)
                self.message_display.show_message("NORMAL GRAVITY!", 1)
             # Implementing a Restart
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.current_level -=1
                pg.time.set_timer(LOAD_NEW_LEVEL,100)
            # Implementing a pause
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.is_paused = not self.is_paused
                self.message_display.show_message("PAUSED!", 1)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_down = True
                # Get mouse position and start a new dynamic line
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.current_line = dynamic_item.DynamicItem(self.space, 'blue')
                self.current_line.add_vertex(mouse_x, mouse_y)
                
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_down = False
                if self.current_line:
                    self.drawing_lines.append(self.current_line)
                    self.current_line = None
                
            elif event.type == pg.MOUSEMOTION and self.mouse_down:
                # Get mouse position
                mouse_x, mouse_y = pg.mouse.get_pos()
                if mouse_x == 0 or mouse_x == WIDTH or mouse_y == 0 or mouse_y == HEIGHT:
                    self.mouse_down = False
                if self.current_line and self.iter % 10 == 0:
                    self.current_line.add_vertex(mouse_x, mouse_y)

            elif event.type == START_FLOW:
                self.level_grain_dropping = True
                # Disable the timer after the first trigger
                pg.time.set_timer(START_FLOW, 0)
                
            elif event.type == LOAD_NEW_LEVEL:
                pg.time.set_timer(LOAD_NEW_LEVEL, 0)  # Clear the timer
                self.intro_image = None
                self.current_level += 1
                if not self.load_level(self.current_level):
                    self.message_display.show_message("You Win!", 5)  # End of game message
                    pg.time.set_timer(EXIT_APP, 5000)  # Quit game after 5 seconds
                else:
                    if self.current_level == 3 :
                        self.message_display.show_message(f"Level {self.current_level} Start! PINK Is Bouncy !!", 2)
                    elif self.current_level == 4:
                        self.message_display.show_message( "TORNADO ACTIVE USING ARROW!", 4)
                    else:
                        self.message_display.show_message(f"Level {self.current_level} Start!", 2)

            # Start Tornado with 'T' key
            elif event.type == pg.KEYDOWN and event.key == pg.K_RIGHT and not self.tornado_active:
                self.tornado_active = True
                self.space.gravity = (5, 3)  # Tornado effect
                pg.time.set_timer(TORNADOR, 2000)  # Schedule the Tornado to stop after 2 seconds

            # Stop Tornado effect
            elif event.type == TORNADOR:
                self.tornado_active = False
                self.space.gravity = (0,-9.8)   # Reset gravity
                pg.time.set_timer(TORNADOR, 0) 

             # Start Tornado with 'T' key
            elif event.type == pg.KEYDOWN and event.key == pg.K_LEFT and not self.tornado_active:
                self.tornado_active = True
                self.space.gravity = (-5, 3)  # Tornado effect
                pg.time.set_timer(TORNADOL, 2000)  # Schedule the Tornado to stop after 2 seconds

            # Stop Tornado effect
            elif event.type == TORNADOL:
                self.tornado_active = False
                self.space.gravity = (0,-9.8)   # Reset gravity
                pg.time.set_timer(TORNADOL, 0) 

            
                
                    
    def run(self):
        '''Run the main game loop'''
        while True:
            self.check_events()
            self.update()
            self.draw()

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()


