import pygame
from pygame.math import Vector2
import random
from population import Population
from brain import NeuralNetwork
from creature import Creature, CreatureB
from place import Place
from food import get_food_info, Berry, BerryClusterer
#
#import cProfile, pstats, io
#
#pr = cProfile.Profile()
#pr.enable()
#

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

berry_clusterer = BerryClusterer(8, WIDTH, HEIGHT)
berries = [
    berry_clusterer.spawn_berry(),
    berry_clusterer.spawn_berry(),
    berry_clusterer.spawn_berry(),
    berry_clusterer.spawn_berry()
]

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
            berries[0].pos = Vector2(x, y)
            tick = 0

    # Logic
    for pop in populations:
        for creature in pop:
            closest = []

            target_data = min(
                # hack the (direction, distance, berry) into a tuple:
                (get_food_info(creature, b.pos) + (b,) for b in berries), 
                key=lambda x: x[1], # <-- grab the closest to us
                default=None
            )

            if target_data:
                direction, distance, target_berry = target_data # Unpack
                creature.update(direction, distance)

                if distance < Berry.SIZE:
                    # EATEN!
                    berry_clusterer.move(target_berry)


    if (generation < 30 and tick > MAX_AGE) or (tick > MAX_AGE2):
        tick = 0
        for i in range(len(populations)):
            populations[i].new_creatures()
            populations[i].place()

        generation += 1

    if render:
        # Rendering
        screen.fill(WHITE)
        total_creatures = 0
        for pop in populations:
            total_creatures += len(pop)
            for c in pop:
                c.draw(screen)
        
        for berry in berries:
            berry.draw(screen)
        
        fps = clock.get_fps()
        fps_surf = font.render(f"FPS: {fps:.1f}  |  Creatures: {total_creatures}, generation: {generation}", True, (0, 0, 0))
        screen.blit(fps_surf, (8, 8))
        
        pygame.display.flip()
        clock.tick(60) # 60 FPS
    tick += 1

    #if tick > 60*5:
    #    break


#pr.disable()
    
# Print sorted results
#s = io.StringIO()
#ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats('cumulative')
#ps.print_stats(20)  # top 20 functions
#print(s.getvalue())

pygame.quit()