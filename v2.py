import pygame
from pygame.math import Vector2
import random
from population import Population
from brain import NeuralNetwork
from creature import Creature, CreatureB
from place import Place
from food import get_food_info, Food

# JG - there is more code in your folder [admin/01-creatures/v2]


# Constants
WIDTH, HEIGHT = 1530, 880
#WIDTH, HEIGHT = 2500, 1400 # demo day

WHITE = (255, 255, 255)

POPULATION = 211
MAX_AGE = 432
MAX_AGE2 = 1024
SCREEN_CENTER = Vector2(WIDTH // 2, HEIGHT // 2)


# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18, bold=True)


pop_a = Population(
    size              = POPULATION,
    creature_factory  = lambda: Creature(),
    placement_manager = Place(POPULATION, SCREEN_CENTER, WIDTH, HEIGHT)
)

pop_b = Population(
    size              = POPULATION,
    creature_factory  = lambda: CreatureB(),
    placement_manager = Place(POPULATION, SCREEN_CENTER, WIDTH, HEIGHT)
)

populations = [pop_a, pop_b]


food = Food(WIDTH, HEIGHT)
generation = 0
tick = 0
running = True
render = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                render = not render

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get mouse position
            x, y = pygame.mouse.get_pos()
            print(f"Mouse clicked at: ({x}, {y})")
            food.pos = Vector2(x, y)
            tick = 0

    # Logic
    for pop in populations:
        for creature in pop:
            direction, distance = get_food_info(creature, food.pos)
            creature.update(direction, distance)

            if distance < food.size():
                food.move()

    if (generation < 30 and tick > MAX_AGE) or (tick > MAX_AGE2):
        tick = 0
        for i in range(len(populations)):
            populations[i].new_creatures()
            populations[i].place()

        generation += 1

        if generation % 4 == 0:
            food.move()

    if render:
        # Rendering
        screen.fill(WHITE)
        total_creatures = 0
        for pop in populations:
            total_creatures += len(pop)
            for c in pop:
                c.draw(screen)
        
        #pygame.draw.line(screen, (250,0,0), ((WIDTH // 2)-20, (HEIGHT // 2)), ((WIDTH // 2)+20, (HEIGHT // 2)), 1)
        #pygame.draw.line(screen, (250,0,0), ((WIDTH // 2), (HEIGHT // 2)-20), ((WIDTH // 2), (HEIGHT // 2)+20), 1)
        food.draw(screen)
        
        fps = clock.get_fps()
        fps_surf = font.render(f"FPS: {fps:.1f}  |  Creatures: {total_creatures}, generation: {generation}", True, (0, 0, 0))
        screen.blit(fps_surf, (8, 8))
        
        pygame.display.flip()
        clock.tick(60) # 60 FPS
    tick += 1

pygame.quit()