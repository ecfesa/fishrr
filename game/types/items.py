from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import random

class FishableType(Enum):
    FISH = "fish"
    TRASH = "trash"

class FishDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"

# New Generic Item base class
@dataclass
class Item(ABC):
    name: str
    weight: float  # in kg

    @abstractmethod
    def get_description(self) -> str:
        pass

# FishableItem now inherits from Item
@dataclass
class FishableItem(Item):
    # name: str (inherited from Item)
    # weight: float (inherited from Item)
    type: FishableType
    rarity: float  # 0.0 to 1.0
    
    # get_description is inherited as abstract and should be implemented by subclasses

@dataclass
class Fish(FishableItem):
    # Inherited: name, weight, type, rarity
    species: str
    difficulty: FishDifficulty
    
    def __init__(self, name: str, species: str, rarity: float, weight: float, difficulty: FishDifficulty = FishDifficulty.MEDIUM):
        # FishableItem's dataclass __init__ expects: name, weight, type, rarity
        super().__init__(name=name, weight=weight, type=FishableType.FISH, rarity=rarity)
        self.species = species
        self.difficulty = difficulty
    
    def get_description(self) -> str:
        return f"Caught a {self.name} ({self.species})!\nWeight: {self.weight:.2f}kg\nDifficulty: {self.difficulty.value.capitalize()}"

@dataclass
class TrashItem(FishableItem):
    # Inherited: name, weight, type, rarity

    def __init__(self, name: str, rarity: float, weight: float):
        # FishableItem's dataclass __init__ expects: name, weight, type, rarity
        super().__init__(name=name, weight=weight, type=FishableType.TRASH, rarity=rarity)
    
    def get_description(self) -> str:
        return f"Found some trash: {self.name}"

# Predefined items with more balanced rarity values
AVAILABLE_FISH = [
    # Easy fish - higher rarity values (more common)
    lambda: Fish("Common Carp", "Cyprinus carpio", 0.8, random.uniform(1.0, 3.0), FishDifficulty.EASY),
    lambda: Fish("Sardine", "Sardina pilchardus", 0.75, random.uniform(0.1, 0.3), FishDifficulty.EASY),
    lambda: Fish("Bluegill", "Lepomis macrochirus", 0.7, random.uniform(0.2, 0.5), FishDifficulty.EASY),
    
    # Medium fish - medium rarity
    lambda: Fish("Rainbow Trout", "Oncorhynchus mykiss", 0.6, random.uniform(0.5, 2.0), FishDifficulty.MEDIUM),
    lambda: Fish("Bass", "Micropterus", 0.55, random.uniform(0.8, 3.0), FishDifficulty.MEDIUM),
    lambda: Fish("Catfish", "Siluriformes", 0.5, random.uniform(1.0, 6.0), FishDifficulty.MEDIUM),
    
    # Hard fish - lower rarity (less common)
    lambda: Fish("Tuna", "Thunnus", 0.4, random.uniform(10.0, 30.0), FishDifficulty.HARD),
    lambda: Fish("Salmon", "Salmo salar", 0.35, random.uniform(3.0, 7.0), FishDifficulty.HARD),
    
    # Legendary fish - very rare
    lambda: Fish("Legendary Sturgeon", "Acipenser", 0.2, random.uniform(30.0, 80.0), FishDifficulty.LEGENDARY),
    lambda: Fish("Golden Koi", "Cyprinus carpio", 0.15, random.uniform(5.0, 15.0), FishDifficulty.LEGENDARY),
]

# Balanced trash items (slightly less common than easy fish)
AVAILABLE_TRASH = [
    lambda: TrashItem("Old Boot", 0.65, 0.5),
    lambda: TrashItem("Tin Can", 0.65, 0.2),
    lambda: TrashItem("Seaweed", 0.7, 0.1),
    lambda: TrashItem("Plastic Bottle", 0.6, 0.3),
]
    
    