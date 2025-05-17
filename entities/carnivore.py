from .base import Entity, Movable, Consumable, Reproducible
from .herbivore import Herbivore
import random, time 

class Carnivore(Entity, Movable, Consumable, Reproducible):
    def __init__(self, x, y, health=12, age=0, lifespan=250, hunger=7, food_value=7):
        super().__init__(x, y, health, age, lifespan)
        self.hunger = hunger
        self._food_value = food_value
        self.last_reproduce_time = 0

    @property
    def food_value(self):
        return self._food_value

    def move(self, world):
        from .herbivore import Herbivore
        import time

        # 1) Hunting: eat any herbivore in the four adjacent cells
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            tx, ty = self.x + dx, self.y + dy
            if 0 <= tx < world.width and 0 <= ty < world.height:
                occ = world.grid[tx][ty]
                prey_list = [e for e in occ if isinstance(e, Herbivore)]
                if prey_list:
                    # Kill the first found prey and move in
                    world.consume(self, prey_list[0])
                    world.move_entity(self, tx, ty)
                    return

        # 2) Reproduction: if both parents are ready (and off cooldown)
        if self.can_reproduce(world):
            now = time.time()
            if now - self.last_reproduce_time >= world.reproduce_cooldown:
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    px, py = self.x + dx, self.y + dy
                    if not (0 <= px < world.width and 0 <= py < world.height):
                        continue
                    for other in world.grid[px][py]:
                        if (isinstance(other, Carnivore)
                                and other.can_reproduce(world)
                                and now - other.last_reproduce_time >= world.reproduce_cooldown):
                            # find an empty cell next to either parent
                            cx, cy = world.find_empty_adjacent(self.x, self.y)
                            if cx is None:
                                cx, cy = world.find_empty_adjacent(other.x, other.y)
                            if cx is not None:
                                child = Carnivore(cx, cy)
                                world.add_entity(child)
                                self.last_reproduce_time = now
                                other.last_reproduce_time = now
                            return

        # 3) Chase: move one step toward the nearest herbivore, eating if you land on it
        prey = world.find_nearest(self, Herbivore)
        if prey:
            dx = (prey.x - self.x)
            dy = (prey.y - self.y)
            dx = (dx > 0) - (dx < 0)
            dy = (dy > 0) - (dy < 0)
            tx, ty = self.x + dx, self.y + dy
            if 0 <= tx < world.width and 0 <= ty < world.height:
                occ = world.grid[tx][ty]
                # if you move onto a herbivore, eat it
                prey_list = [e for e in occ if isinstance(e, Herbivore)]
                if prey_list:
                    world.consume(self, prey_list[0])
                    world.move_entity(self, tx, ty)
                    return
                # otherwise only step into an empty cell
                if not any(isinstance(e, Carnivore) for e in occ):
                    world.move_entity(self, tx, ty)
                    return

        # 4) Wander: try up to 4 random directions into empty only
        for dx, dy in random.sample([(1,0),(-1,0),(0,1),(0,-1)], 4):
            tx, ty = self.x + dx, self.y + dy
            if not (0 <= tx < world.width and 0 <= ty < world.height):
                continue
            occ = world.grid[tx][ty]
            if not occ:  # truly empty
                world.move_entity(self, tx, ty)
                return

        # 5) Stuck: no valid move this tick
        

    # ↓ Use dynamic threshold from the slider ↓
    def can_reproduce(self, world):
        return self.hunger < world.carn_reproduce_threshold and self.health > 6

    def reproduce(self, partner, world):
        nx, ny = world.find_empty_adjacent(self.x, self.y)
        if nx is not None:
            child = Carnivore(nx, ny)
            world.add_entity(child)

    # ↓ Full tick() with reproduction check ↓
    def tick(self, world):
        # 1) Age, hunger, health decay
        self.age += 1
        self.hunger += 1
        self.health -= 0.7

        # 2) Death by old age or zero health
        if self.age >= self.lifespan or self.health <= 0:
            world.remove_entity(self)
            return

        # 3) Hunting: eat adjacent herbivore if present
        prey = world.find_nearest(self, Herbivore)
        if prey and world.distance(self, prey) == 1:
            world.consume(self, prey)
            self.hunger = 0
            self.health += prey.food_value
        else:
            # 4) Otherwise move
            self.move(world)

        # 5) Reproduction with 5s cooldown
        if self.can_reproduce(world):
            now = time.time()
            if now - self.last_reproduce_time >= world.reproduce_cooldown:
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nx, ny = self.x + dx, self.y + dy
                    if not (0 <= nx < world.width and 0 <= ny < world.height):
                        continue
                    for other in world.grid[nx][ny]:
                        if (isinstance(other, Carnivore)
                                and other.can_reproduce(world)
                                and now - other.last_reproduce_time >= world.reproduce_cooldown):
                            self.reproduce(other, world)
                            self.last_reproduce_time = now
                            other.last_reproduce_time = now
                            return
