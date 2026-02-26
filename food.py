import pygame
from pygame.math import Vector2
import random
import math

FOOD_SIZE = 8

class Food:
    def __init__(self, width, height):
        self.pos = Vector2(width // 2, height // 2)
        # pos = Vector2(0, 0)
        self._size = FOOD_SIZE
        self.screen_size = Vector2(width, height)

    def size(self):
        return self._size
    
    def move(self):
        ##
        ## Ugh, I wonder how many loops this will do in the worst case?
        ##
        while True:
            new_x = random.randint(0, int(self.screen_size.x))
            new_y = random.randint(0, int(self.screen_size.y))

            # Calculate Euclidean distance
            distance = math.hypot(new_x - self.pos.x, new_y - self.pos.y)

            if distance >= 256:
                self.pos = Vector2(new_x, new_y)
                return

    def draw(self, screen):
        pygame.draw.circle(screen, (100, 255, 100), self.pos, self._size)


def get_food_info(c, food):
    tmp = Vector2(1, 0).rotate(c.angle)
    pos = Vector2(c.pos.x, c.pos.y)

    # angle_to is very weird - we need to fix it between -180 and 180
    a = tmp.angle_to(food-pos)
    if a < -180:
        a = 360 + a

    return a, pos.distance_to(food)