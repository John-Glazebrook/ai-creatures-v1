
class Population:
    def __init__(self, size, creature_factory):
        self.size = size
        self.creatures = [creature_factory() for _ in range(size)]
        self.creature_factory = creature_factory

    def __iter__(self):
        return iter(self.creatures)
    
    def __len__(self):
        return len(self.creatures)