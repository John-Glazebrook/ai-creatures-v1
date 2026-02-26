import pygame
from pygame.math import Vector2
import random
from brain import NeuralNetwork
from creature import Creature
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

def place_creatures(creatures):
    strategies = [place_in_circle, place_ontop, place_randomly]
    weights = [10, 30, 60]

    # random.choices returns a list, so we take the first element [0]
    selected_task = random.choices(strategies, weights=weights, k=1)[0]
    selected_task(creatures)


def place_in_circle(creatures):
    dist = random.gauss(240, 100)
    angle = random.randint(0, 360)
    angle_delta = 360 / POPULATION

    for c in creatures:
        clock_hand = Vector2(dist, 0).rotate(angle)
        c.pos = SCREEN_CENTER+clock_hand
        c.angle = angle

        angle += angle_delta

def place_randomly(creatures):
    for c in creatures:
        x = random.randint(10, WIDTH-20)
        y = random.randint(10, HEIGHT-20)
        angle = random.randint(0, 360)
        c.pos = Vector2(x, y)
        c.angle = angle
        
def place_ontop(creatures):
    x = random.randint(10, WIDTH-20)
    y = random.randint(10, HEIGHT-20)
    angle = random.randint(0, 360)

    for c in creatures:    
        c.pos = Vector2(x, y)
        c.angle = angle

# Constants
WIDTH, HEIGHT = 900, 900
WHITE = (255, 255, 255)

POPULATION = 60
MAX_AGE = 432
SCREEN_CENTER = Vector2(WIDTH // 2, HEIGHT // 2)


# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


#dist = random.gauss(240, 100)
#angle = random.randint(0, 360)
#angle_delta = 360 / POPULATION

creatures = []
for i in range(POPULATION):

    if i==0:
        c = Creature(SCREEN_CENTER, (186,85,250))
    else:
        c = Creature(SCREEN_CENTER)

    creatures.append(c)


place_in_circle(creatures)

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
    for creature in creatures:
        direction, distance = get_food_info(creature, food.pos)
        creature.update(direction, distance)

        if distance < food.size():
            food.move()

    if tick > MAX_AGE:
        tick = 0
        creatures = new_creatures(creatures)
       
        for c in creatures:
            c.score = 0

        place_creatures(creatures)
        generation += 1

        if generation % 4 == 0:
            food.move()

    if render:
        # Rendering
        screen.fill(WHITE)
        for c in creatures:
            c.draw(screen)
        
        #pygame.draw.line(screen, (250,0,0), ((WIDTH // 2)-20, (HEIGHT // 2)), ((WIDTH // 2)+20, (HEIGHT // 2)), 1)
        #pygame.draw.line(screen, (250,0,0), ((WIDTH // 2), (HEIGHT // 2)-20), ((WIDTH // 2), (HEIGHT // 2)+20), 1)
        food.draw(screen)
        
        
        pygame.display.flip()
        clock.tick(60) # 60 FPS
    tick += 1

pygame.quit()