from .base import Entity, Consumable
import random

class Vegetation(Entity, Consumable):
    def __init__(self, x, y, health=5, age=0, lifespan=100, food_value=3):
        super().__init__(x, y, health, age, lifespan)
        self._food_value = food_value

    @property
    def food_value(self):
        return self._food_value

    def tick(self, world):
        # Age and health changes
        self.age += 1
        if self.age >= self.lifespan:
            world.remove_entity(self)
        # Passive growth: occasional health regen
        if random.random() < 0.1:
            self.health = min(self.health + 1, 10)