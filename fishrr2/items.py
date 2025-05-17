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

# Generic Item base class
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
    type: FishableType
    rarity: float  # 0.0 to 1.0
    
    # get_description is inherited as abstract and should be implemented by subclasses

@dataclass
class Fish(FishableItem):
    species: str
    difficulty: FishDifficulty
    
    def __init__(self, name: str, species: str, rarity: float, weight: float, difficulty: FishDifficulty = FishDifficulty.MEDIUM):
        super().__init__(name=name, weight=weight, type=FishableType.FISH, rarity=rarity)
        self.species = species
        self.difficulty = difficulty
    
    def get_description(self) -> str:
        return f"Caught a {self.name} ({self.species})! Weight: {self.weight:.2f}kg. Difficulty: {self.difficulty.value.capitalize()}."

@dataclass
class TrashItem(FishableItem):
    def __init__(self, name: str, rarity: float, weight: float):
        super().__init__(name=name, weight=weight, type=FishableType.TRASH, rarity=rarity)
    
    def get_description(self) -> str:
        return f"Ugh, it's just a {self.name}. Weight: {self.weight:.2f}kg."

# Predefined items with more balanced rarity values
AVAILABLE_FISH = [
    # Easy fish - higher rarity values (more common)
    lambda: Fish(name="Common Carp", species="Cyprinus carpio", rarity=0.8, weight=random.uniform(1.0, 3.0), difficulty=FishDifficulty.EASY),
    lambda: Fish(name="Sardine", species="Sardina pilchardus", rarity=0.75, weight=random.uniform(0.1, 0.3), difficulty=FishDifficulty.EASY),
    lambda: Fish(name="Bluegill", species="Lepomis macrochirus", rarity=0.7, weight=random.uniform(0.2, 0.5), difficulty=FishDifficulty.EASY),
    
    # Medium fish - medium rarity
    lambda: Fish(name="Rainbow Trout", species="Oncorhynchus mykiss", rarity=0.6, weight=random.uniform(0.5, 2.0), difficulty=FishDifficulty.MEDIUM),
    lambda: Fish(name="Bass", species="Micropterus", rarity=0.55, weight=random.uniform(0.8, 3.0), difficulty=FishDifficulty.MEDIUM),
    lambda: Fish(name="Catfish", species="Siluriformes", rarity=0.5, weight=random.uniform(1.0, 6.0), difficulty=FishDifficulty.MEDIUM),
    
    # Hard fish - lower rarity (less common)
    lambda: Fish(name="Tuna", species="Thunnus", rarity=0.4, weight=random.uniform(10.0, 30.0), difficulty=FishDifficulty.HARD),
    lambda: Fish(name="Salmon", species="Salmo salar", rarity=0.35, weight=random.uniform(3.0, 7.0), difficulty=FishDifficulty.HARD),
    
    # Legendary fish - very rare
    lambda: Fish(name="Legendary Sturgeon", species="Acipenser", rarity=0.2, weight=random.uniform(30.0, 80.0), difficulty=FishDifficulty.LEGENDARY),
    lambda: Fish(name="Golden Koi", species="Cyprinus carpio", rarity=0.15, weight=random.uniform(5.0, 15.0), difficulty=FishDifficulty.LEGENDARY),
]

# Balanced trash items (slightly less common than easy fish)
AVAILABLE_TRASH = [
    lambda: TrashItem(name="Old Boot", rarity=0.65, weight=0.5),
    lambda: TrashItem(name="Tin Can", rarity=0.65, weight=0.2),
    lambda: TrashItem(name="Seaweed", rarity=0.7, weight=0.1),
    lambda: TrashItem(name="Plastic Bottle", rarity=0.6, weight=0.3),
]