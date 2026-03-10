import pygame
from pygame.math import Vector2
import random
from population import Population
from brain import NeuralNetwork
from creature import Creature, CreatureB
from place import Place
from food import get_food_info, Food

# JG - there is more code in your folder [admin/01-creatures/v2]

def new_creatures(creatures):
    print("----- NEW CREATURES -----")
    kids = []
    tmp = sorted(creatures, key=lambda c: c.score)
    tmp.reverse()
    for c in tmp:
        print(c.score)

    # breed the top 50% of creatures
    # then replace the bottom 50% with these
    for i in range(len(tmp) // 2):
        p1 = tmp[i]
        p2 = tmp[random.randint(0, len(tmp)//2)]
            
        childbrain = NeuralNetwork.breed(p1.brain, p2.brain, mutation_rate=1.2, mutation_range=0.15)
        c = Creature()
        c.brain = childbrain
        kids.append(c)

    creatures = []
    for i in range(len(tmp) // 2):
        creatures.append(tmp[i])
    for kid in kids:
        creatures.append(kid)
    for c in creatures:
        c.score = 0
    print("----- END NEW CREATURES -----")
    return creatures


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


#creatures = []
#creaturesb = []
#for i in range(POPULATION):
#    c = Creature()
#    creatures.append(c)
#    creaturesb.append(CreatureB())

pop_a = Population(
    size=POPULATION,
    creature_factory=lambda: Creature()
)

pop_b = Population(
    size=POPULATION,
    creature_factory=lambda: CreatureB()
)

populations = [pop_a, pop_b]

place = Place(POPULATION, SCREEN_CENTER, WIDTH, HEIGHT)

for pop in populations:
    place.in_circle(pop)

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

    if (generation < 30 and tick > MAX_AGE) or (tick > MAX_AGE2) and False:
        tick = 0
        for i in range(len(populations)):
            creatures = new_creatures(populations[i])
       
            #for c in creatures:
            #    c.score = 0

            populations[i] = creatures

            place.creatures(populations[i])
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