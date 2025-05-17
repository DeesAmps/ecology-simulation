# world.py
import random
from entities.vegetation import Vegetation
from entities.herbivore import Herbivore
from entities.carnivore import Carnivore

class World:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # slider‑driven parameters
        self.reproduce_cooldown      = 4.0
        self.plant_spawn_rate         = 0.02
        self.herb_reproduce_threshold = 8.0
        self.carn_reproduce_threshold = 8.0
        self.max_herbivores           = 500   
        self.initial_plants           = 500
        self.initial_herb_count      = 200
        self.initial_carn_count      = 20
        self.entities = []
        self.grid = [[[] for _ in range(height)] for _ in range(width)]

    def add_entity(self, entity):
        self.entities.append(entity)
        self.grid[entity.x][entity.y].append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
        cell = self.grid[entity.x][entity.y]
        if entity in cell:
            cell.remove(entity)

    def move_entity(self, entity, new_x, new_y):
        # 1) bounds check
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return

        # 2) safe‐remove from old cell
        old_x, old_y = entity.x, entity.y
        try:
            self.grid[old_x][old_y].remove(entity)
        except (ValueError, IndexError):
            pass

        # 3) update position & insert into new cell
        entity.x, entity.y = new_x, new_y
        self.grid[new_x][new_y].append(entity)

    def find_empty_adjacent(self, x: int, y: int):
        neighbors = [(x+dx, y+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
        random.shuffle(neighbors)
        for nx, ny in neighbors:
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[nx][ny]:
                    return nx, ny
        return None, None

    def distance(self, a, b) -> int:
        return abs(a.x - b.x) + abs(a.y - b.y)

    def find_nearest(self, entity, cls_type):
        nearest = None
        min_dist = float('inf')
        for other in self.entities:
            if isinstance(other, cls_type) and other is not entity:
                dist = self.distance(entity, other)
                if dist < min_dist:
                    min_dist, nearest = dist, other
        return nearest

    def consume(self, eater, eaten):
        eater.health += eaten.food_value
        self.remove_entity(eaten)

    def occupants(self, x, y):
        """Return list of entities at (x,y) or [] if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return []

    def tick(self):
        # 1) Vegetation spawning
        for x in range(self.width):
            for y in range(self.height):
                if not self.grid[x][y] and random.random() < self.plant_spawn_rate:
                    self.add_entity(Vegetation(x, y))

        # 2) Update each entity
        for entity in self.entities[:]:
            # ENFORCE herbivore cap before tick
            if isinstance(entity, Herbivore):
                count = sum(isinstance(e, Herbivore) for e in self.entities)
                if count >= self.max_herbivores:
                    continue
            entity.tick(self)
