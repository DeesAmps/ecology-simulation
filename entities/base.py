from abc import ABC, abstractmethod

class Entity(ABC):
    """
    Shared state and life cycle for all entities.
    """
    def __init__(self, x: int, y: int, health: float, age: int, lifespan: int):
        self.x = x
        self.y = y
        self.health = health
        self.age = age
        self.lifespan = lifespan

    @abstractmethod
    def tick(self, world):
        """Update entity state each simulation tick."""
        pass

class Movable(ABC):
    """Contract for entities that can move around the grid."""
    @abstractmethod
    def move(self, world):
        pass

class Consumable(ABC):
    """Contract for entities that can be consumed for food."""
    @property
    @abstractmethod
    def food_value(self) -> float:
        pass

class Reproducible(ABC):
    """Contract for entities capable of reproducing."""
    @abstractmethod
    def can_reproduce(self) -> bool:
        pass

    @abstractmethod
    def reproduce(self, partner, world):
        pass