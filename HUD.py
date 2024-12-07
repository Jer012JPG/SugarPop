from settings import *
import pygame

class hud:
    def __init__(self, screen, font, level, buckets, static_buckets, total_sugar_count,sugar_grains):
        self.screen = screen
        self.font = font
        self.level = level
        self.buckets = buckets
        self.Static_buckets = static_buckets
        self.total_sugar_count = total_sugar_count
        self.current_level = level  # Assuming the level data is a dict with a 'level' key
        self.sugar_grains = sugar_grains

    def draw_hud(self):
        """Draw the HUD displaying the number of grains."""

        if self.total_sugar_count is not None:
            # Render the current level text
            level_surface = self.font.render(f'Level {self.current_level}', True, (255, 255, 255))
            self.screen.blit(level_surface, (10, 10))

            # Render the remaining sugar grains text
            remaining_grains = self.total_sugar_count - len(self.sugar_grains)  # Assuming self.sugar_grains is a list
            sugar_surface = self.font.render(f'Sugar Left: {remaining_grains}', True, (255, 255, 255))
            self.screen.blit(sugar_surface, (10, 50))

            # Display the count for each dynamic bucket
            for bucket, bucket_data in zip(self.buckets, self.level['data']['buckets']):
                bucket_status = self.font.render(f'{bucket.count}/{bucket.needed_sugar}', True, (255, 255, 255))
                self.screen.blit(bucket_status, (bucket_data['x'] - 20, HEIGHT - bucket_data['y'] - 30))

            # Display the count for each static bucket (if any)
            for i in range(len(self.Static_buckets)):
                staticbucket = self.Static_buckets[i]
                for bucket, bucket_data in zip(self.Static_buckets, self.level['data'].get('Static_buckets', [])):
                    bucket_status = self.font.render(f'{staticbucket.count}', True, (255, 255, 255))
                    self.screen.blit(bucket_status, (bucket_data['x'] - 20, HEIGHT - bucket_data['y'] - 30))



         
