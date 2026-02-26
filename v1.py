import pygame
import random

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
PINK = (255, 105, 180)

class Creature:
    def __init__(self):
        # Start in the middle of the screen
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        
        # Random speed between -3 and +8
        #self.speed = random.uniform(-3, 8)
        #self.speed = random.uniform(2, 4)
        self.speed = 0.3
        
        # Random angle in degrees (0 to 360)
        #self.angle = random.uniform(0, 360)
        self.angle = 270
        
        # Create the visual "arrow" (a simple polygon)
        # We point it to the right (0 degrees) by default
       # self.original_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        ## our nose is at 0, 0
        #pygame.draw.polygon(self.original_surf, PINK, [(0, 30), (80, 0), (80, 60)])

        self.original_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        center = 100  # Center of the 20x20 surface

        # nose at center (10, 10), pointing right
        pygame.draw.polygon(self.original_surf, PINK, [
            (center, center),           # nose
            (center - 60, center - 20),
            (center - 53, center),
            (center - 60, center + 20)
        ])


        

    def update(self):
        # Create a direction vector from our angle
        # In Pygame, 0 degrees is to the right
        velocity = pygame.math.Vector2(1, 0).rotate(self.angle) * self.speed
        self.pos += velocity

        self.angle += 1


    def draw(self, screen):
        # Note: rotate() is counter-clockwise, so we use -self.angle
        #rotated_surf = pygame.transform.rotate(self.original_surf, -self.angle)
        rotated_surf = pygame.transform.rotate(self.original_surf, -self.angle)
        rect = rotated_surf.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(rotated_surf, rect)


# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
creature = Creature()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Logic
    creature.update()

    # Rendering
    screen.fill(WHITE)
    creature.draw(screen)
    
    pygame.draw.line(screen, (250,0,0), ((WIDTH // 2)-20, (HEIGHT // 2)), ((WIDTH // 2)+20, (HEIGHT // 2)), 1)
    pygame.draw.line(screen, (250,0,0), ((WIDTH // 2), (HEIGHT // 2)-20), ((WIDTH // 2), (HEIGHT // 2)+20), 1)
    
    pygame.display.flip()
    clock.tick(60) # 60 FPS

pygame.quit()