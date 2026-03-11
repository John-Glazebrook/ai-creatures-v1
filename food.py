import pygame
from pygame.math import Vector2
import random
import math

FOOD_SIZE = 8

import random
import math

class Berry:
    SIZE = FOOD_SIZE

    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self._size = FOOD_SIZE

    def size(self):
        return self._size

    def draw(self, screen):
        pygame.draw.circle(screen, (100, 255, 100), self.pos, self._size)
    
    def __repr__(self):
        return f"Berry(x={self.pos.x:.1f}, y={self.pos.y:.1f})"


class BerryClusterer:
    def __init__(self, count, screen_width, screen_height, radius=40, padding=50):
        self.count = count
        self.sw = screen_width
        self.sh = screen_height
        self.radius = radius
        self.padding = padding # Keep cluster centers away from the very edge
        self.cluster_rate = 8
        self.cluster_count = 0

        # 68% of berries will be within 20px of the center (1 sigma)
        # 95% of berries will be within 40px of the center (2 sigma)
        # This gives us that nice fading out effect at the edges.
        self.sigma = radius / 2
        
        # Start at a random safe spot
        self.current_center = (
            random.uniform(padding, screen_width - padding),
            random.uniform(padding, screen_height - padding)
        )

    def move_to_new_cluster(self, min_dist=150, max_dist=300):
        # Finds a new cluster center that is 'far away' but still on screen
        found_spot = False
        attempts = 0
        
        while not found_spot and attempts < 100:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(min_dist, max_dist)
            
            new_x = self.current_center[0] + dist * math.cos(angle)
            new_y = self.current_center[1] + dist * math.sin(angle)
            
            # Check if the new center is within our safe bounds
            if (self.padding < new_x < self.sw - self.padding and 
                self.padding < new_y < self.sh - self.padding):
                self.current_center = (new_x, new_y)
                found_spot = True
            
            attempts += 1
            
        # Fallback: if we are trapped in a corner, just pick a random safe spot
        if not found_spot:
            self.current_center = (
                random.uniform(self.padding, self.sw - self.padding),
                random.uniform(self.padding, self.sh - self.padding)
            )

    def spawn_berry(self):
        return self.move(Berry(0, 0))
    
    def move(self, berry:Berry):
        # Spawns a berry with a Gaussian clump around the center
        x = random.gauss(self.current_center[0], self.sigma)
        y = random.gauss(self.current_center[1], self.sigma)
        
        # Final safety clamp: ensures individual berries don't jitter off-screen
        x = max(5, min(self.sw - 5, x))
        y = max(5, min(self.sh - 5, y))

        self.cluster_count += 1
        if self.cluster_count > self.cluster_rate:
            self.cluster_count = 0
            self.move_to_new_cluster()

        berry.pos = Vector2(x, y)

        return berry


def get_food_info(c, berry):
    tmp = Vector2(1, 0).rotate(c.angle)
    pos = Vector2(c.pos.x, c.pos.y)

    # angle_to is very weird - we need to fix it between -180 and 180
    a = tmp.angle_to(berry-pos)
    if a < -180:
        a = 360 + a

    return a, pos.distance_to(berry)