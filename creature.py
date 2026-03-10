import pygame
from pygame.math import Vector2
import random
from brain import NeuralNetwork

PINK = (255, 105, 180)
BLUE = (153, 204, 250)

class Creature:
    colour = PINK
    def __init__(self):
        # Start in the middle of the screen
        self.pos = Vector2(0,0)
        self.speed = 0
        
        # Random angle in degrees (0 to 360)
        #self.angle = random.uniform(0, 360)
        self.angle = 0

        self.brain = NeuralNetwork(input_size=2, hidden_size=16, output_size=2)
        self.score = 0
        
        # Create the visual "arrow" (a simple polygon)
        # our nose is at 0, 0
        self.original_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        center = 16  # Center of the surface

        # nose at center (10, 10), pointing right
        pygame.draw.polygon(self.original_surf, self.colour, [
            (center, center),           # nose
            (center - 20, center - 7),
            (center - 14, center),
            (center - 20, center + 7)
        ])


    def update(self, direction, distance):
       
        angle_delta, speed = self.brain.forward(direction, distance)
        self.angle += angle_delta
        self.angle = self.angle % 360 # normalise the angle

        self.speed = speed

        # Create a direction vector from our angle
        # In Pygame, 0 degrees is to the right
        velocity = pygame.math.Vector2(1, 0).rotate(self.angle) * self.speed
        self.pos += velocity

        self.score += self.distance_to_score(distance)


    def distance_to_score(self, distance, far_cutoff=512, close_cutoff=30, max_score=16):
        if distance > far_cutoff:  # No score
            return 0
        if distance < close_cutoff:   # Very close - max score
            return max_score
            
        x = (far_cutoff - distance) / (far_cutoff - close_cutoff)
        return max_score * (x * x)


    def draw(self, screen):
        # Note: rotate() is counter-clockwise, so we use -self.angle
        #rotated_surf = pygame.transform.rotate(self.original_surf, -self.angle)
        rotated_surf = pygame.transform.rotate(self.original_surf, -self.angle)
        rect = rotated_surf.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(rotated_surf, rect)


class CreatureB(Creature):
    colour = BLUE