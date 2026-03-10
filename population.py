import random
from brain import NeuralNetwork


class Population:
    def __init__(self, size, creature_factory, placement_manager):
        self.size = size
        self.creature_factory = creature_factory
        self.placement_manager = placement_manager
        #
        self.creatures = [creature_factory() for _ in range(size)]
        placement_manager.in_circle(self.creatures)

    def place(self):
        self.placement_manager.creatures(self)

    def __iter__(self):
        return iter(self.creatures)
    
    def __len__(self):
        return len(self.creatures)
    
    def new_creatures(self):
        print("----- NEW CREATURES -----")
        kids = []
        tmp = sorted(self.creatures, key=lambda c: c.score)
        tmp.reverse()
        for c in tmp:
            print(c.score)

        # breed the top 50% of creatures
        # then replace the bottom 50% with these
        for i in range(len(tmp) // 2):
            p1 = tmp[i]
            p2 = tmp[random.randint(0, len(tmp)//2)]
                
            childbrain = NeuralNetwork.breed(p1.brain, p2.brain, mutation_rate=1.2, mutation_range=0.15)
            #c = Creature()
            c = self.creature_factory()
            c.brain = childbrain
            kids.append(c)

        self.creatures = []
        for i in range(len(tmp) // 2):
            self.creatures.append(tmp[i])
        for kid in kids:
            self.creatures.append(kid)
        for c in self.creatures:
            c.score = 0
        print("----- END NEW CREATURES -----")
        
