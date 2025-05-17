from .base import Entity, Movable, Consumable, Reproducible
from .vegetation import Vegetation
import random, time

class Herbivore(Entity, Movable, Consumable, Reproducible):
    FLEE_DISTANCE = 5  # Distance to flee from carnivores
    GROUP_DISTANCE = 10  # Distance to group with other herbivores
    def __init__(self, x, y, health=10, age=0, lifespan=200, hunger=5, food_value=5):
        super().__init__(x, y, health, age, lifespan)
        self.hunger = hunger
        self._food_value = food_value
        self.last_reproduce_time = 0
        self.last_move_time = 0

    @property
    def food_value(self):
        return self._food_value

    def move(self, world):
        from .carnivore import Carnivore
        from .vegetation import Vegetation

        # 1) Evade nearest predator
        predator = world.find_nearest(self, Carnivore)
        if predator and world.distance(self, predator) <= self.FLEE_DISTANCE:
            dx = (self.x - predator.x)
            dy = (self.y - predator.y)
            dx = (dx > 0) - (dx < 0)
            dy = (dy > 0) - (dy < 0)
            tx, ty = self.x + dx, self.y + dy

            # bounds check
            if 0 <= tx < world.width and 0 <= ty < world.height:
                occ = world.grid[tx][ty]
                # block if another animal there
                if any(isinstance(e, (Herbivore, Carnivore)) for e in occ):
                    return
                # otherwise safe to move
                world.move_entity(self, tx, ty)
            return
        #1a ) If no predator, check for nearest plant
        plant = world.find_nearest(self, Vegetation)
        if plant:
            dist = world.distance(self, plant)
            # if it’s more than one cell away, step toward it
            if dist > 1:
                dx = (plant.x - self.x)
                dy = (plant.y - self.y)
                dx = (dx > 0) - (dx < 0)
                dy = (dy > 0) - (dy < 0)
                tx, ty = self.x + dx, self.y + dy
                # only move if not blocked by another animal
                occ = world.grid[tx][ty]
                if not any(isinstance(e, (Herbivore, Carnivore)) for e in occ):
                    world.move_entity(self, tx, ty)
                    return
            # if dist == 1 you’ll eat it in your tick() logic, so no move needed
        
        # 2) Grouping: move toward nearest herd‑mate
        buddy = world.find_nearest(self, Herbivore)
        if buddy:
            dist = world.distance(self, buddy)
            if 1 < dist <= self.GROUP_DISTANCE:
                dx = (buddy.x - self.x)
                dy = (buddy.y - self.y)
                dx = (dx > 0) - (dx < 0)
                dy = (dy > 0) - (dy < 0)
                tx, ty = self.x + dx, self.y + dy

                if 0 <= tx < world.width and 0 <= ty < world.height:
                    occ = world.grid[tx][ty]
                    # eat plant if present
                    for e in occ:
                        if isinstance(e, Vegetation):
                            world.consume(self, e)
                            world.move_entity(self, tx, ty)
                            return
                    # block if another animal there
                    if any(isinstance(e, (Herbivore, Carnivore)) for e in occ):
                        return
                    world.move_entity(self, tx, ty)
                return

        # 3) Default random wander: pick one random adjacent
        for dx, dy in random.sample([(1,0),(-1,0),(0,1),(0,-1)], 4):
            tx, ty = self.x + dx, self.y + dy
            if not (0 <= tx < world.width and 0 <= ty < world.height):
                continue
            occ = world.grid[tx][ty]
            # if plant, eat & move
            for e in occ:
                if isinstance(e, Vegetation):
                    world.consume(self, e)
                    world.move_entity(self, tx, ty)
                    return
            # skip cells with animals
            if any(isinstance(e, (Herbivore, Carnivore)) for e in occ):
                continue
            # empty → move
            world.move_entity(self, tx, ty)
            return

        # if we get here, no valid move found — stay in place

    # ↓ Updated signature to use dynamic threshold ↓
    def can_reproduce(self, world):
        return self.hunger < world.herb_reproduce_threshold and self.health > 5

    def reproduce(self, partner, world):
        nx, ny = world.find_empty_adjacent(self.x, self.y)
        if nx is not None:
            child = Herbivore(nx, ny)
            world.add_entity(child)

    # ↓ Full tick() with reproduction check dropped in ↓
    def tick(self, world):
        # 1) Age, hunger, health decay
        self.age += 1
        self.hunger += 1
        self.health -= 0.5

        # 2) Death by old age or zero health
        if self.age >= self.lifespan or self.health <= 0:
            world.remove_entity(self)
            return

        # 3) Feeding: eat adjacent plant if present
        plant = world.find_nearest(self, Vegetation)
        if plant and world.distance(self, plant) == 1:
            world.consume(self, plant)
            self.hunger = 0
            self.health += plant.food_value
        else:
            # 4) Otherwise move
            self.move(world)

         # 5) Reproduction with 5s cooldown
        if self.can_reproduce(world):
            now = time.time()
            # only reproduce if this one has waited long enough
            if now - self.last_reproduce_time >= world.reproduce_cooldown:
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nx, ny = self.x + dx, self.y + dy
                    if not (0 <= nx < world.width and 0 <= ny < world.height):
                        continue
                    for other in world.grid[nx][ny]:
                        if (isinstance(other, Herbivore)
                                and other.can_reproduce(world)
                                and now - other.last_reproduce_time >= world.reproduce_cooldown):
                            # spawn one child
                            self.reproduce(other, world)
                            # stamp both parents
                            self.last_reproduce_time = now
                            other.last_reproduce_time = now
                            return
