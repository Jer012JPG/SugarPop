import pygame as pg
import pymunk
from settings import SCALE, HEIGHT, WIDTH
from math import sqrt

class Static_Bucket:
    def __init__(self, space, x, y, width, height):
        """
        Initialize the bucket with an open top by creating three static segments 
        for each wall (left, right, bottom).
        
        :param space: The Pymunk space.
        :param x: X position of the bucket's center in Pygame coordinates.
        :param y: Y position of the bucket's top in Pygame coordinates.
        :param width: Width of the bucket in pixels.
        :param height: Height of the bucket in pixels.
        """
        self.space = space
        self.width = width / SCALE
        self.height = height / SCALE
        self.count = 0  # Counter for collected sugar grains
        

        wall_thickness = 0.2  # Thickness of the walls in physics units

        # Convert Pygame coordinates to Pymunk coordinates
        x_pymunk = x / SCALE
        y_pymunk = y / SCALE # (HEIGHT - y) / SCALE  # Adjust y-coordinate for Pymunk's coordinate system

        # Left wall
        left_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        left_wall_end = (x_pymunk - self.width / 2, y_pymunk + self.height / 2)
        self.left_wall = pymunk.Segment(space.static_body, left_wall_start, left_wall_end, wall_thickness)
        self.left_wall.friction = 0.5
        self.left_wall.elasticity = 0.5
        space.add(self.left_wall)

        # Right wall
        right_wall_start = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        right_wall_end = (x_pymunk + self.width / 2, y_pymunk + self.height / 2)
        self.right_wall = pymunk.Segment(space.static_body, right_wall_start, right_wall_end, wall_thickness)
        self.right_wall.friction = 0.5
        self.right_wall.elasticity = 0.5
        space.add(self.right_wall)

        # Bottom wall
        bottom_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        bottom_wall_end = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        self.bottom_wall = pymunk.Segment(space.static_body, bottom_wall_start, bottom_wall_end, wall_thickness)
        self.bottom_wall.friction = 0.5
        self.bottom_wall.elasticity = 0.5
        space.add(self.bottom_wall)
        

    def draw(self, screen):
        """
        Draw the bucket with an open top on the Pygame screen.
        """
        color = (144, 238, 144)  # Light green color

        # Helper function to convert Pymunk coordinates to Pygame coordinates
        def to_pygame(p):
            return int(p[0] * SCALE), int(HEIGHT - p[1] * SCALE)

        # Draw the bucket edges
        pg.draw.line(screen, color, to_pygame(self.left_wall.a), to_pygame(self.left_wall.b), 2)
        pg.draw.line(screen, color, to_pygame(self.right_wall.a), to_pygame(self.right_wall.b), 2)
        pg.draw.line(screen, color, to_pygame(self.bottom_wall.a), to_pygame(self.bottom_wall.b), 2)

    
        
    def collect(self, sugar_grain):
        """
        Check if a sugar grain is within the bucket bounds and, if so, increase the bucket's count.
        
        :param sugar_grain: The sugar grain to check.
        """
        if self.exploded:
            return  # Don't count grains if the bucket has exploded

        grain_pos = sugar_grain.body.position

        # Get bucket boundaries
        left = self.left_wall.a[0]
        right = self.right_wall.a[0]
        bottom = self.bottom_wall.a[1]
        top = self.left_wall.b[1]

        # Check if the grain's position is within the bucket's bounding box
        if left <= grain_pos.x <= right and bottom <= grain_pos.y <= top:
            self.count += 1
            return True  # Indicate that the grain was collected

        return False  # Grain not collected

