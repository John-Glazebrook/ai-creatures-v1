import random
from pygame.math import Vector2

class Place:
    def __init__(self, population_count, screen_center, width, height):
        self.population_count = population_count
        self.screen_center = screen_center
        self.width = width
        self.height = height

    def creatures(self, creatures):
        strategies = [self.in_circle, self.ontop, self.randomly]
        #weights = [10, 30, 60]
        weights = [0, 30, 0]

        # random.choices returns a list, so we take the first element [0]
        selected_task = random.choices(strategies, weights=weights, k=1)[0]
        selected_task(creatures)


    def in_circle(self, creatures):
        dist = random.gauss(240, 100)
        angle = random.randint(0, 360)
        angle_delta = 360 / self.population_count

        for c in creatures:
            clock_hand = Vector2(dist, 0).rotate(angle)
            c.pos = self.screen_center+clock_hand
            c.angle = angle

            angle += angle_delta

    def randomly(self, creatures):
        for c in creatures:
            x = random.randint(10, self.width-20)
            y = random.randint(10, self.height-20)
            angle = random.randint(0, 360)
            c.pos = Vector2(x, y)
            c.angle = angle

    def ontop(self, creatures):
        x = random.randint(10, self.width-20)
        y = random.randint(10, self.height-20)
        p = Vector2(x, y)
        print("RANDOM ", p)
        angle = random.randint(0, 360)

        for c in creatures:    
            c.pos = Vector2(x, y)
            c.angle = angle