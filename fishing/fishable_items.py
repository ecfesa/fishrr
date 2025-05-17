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

@dataclass
class FishableItem(ABC):
    name: str
    type: FishableType
    rarity: float  # 0.0 to 1.0
    weight: float  # in kg

    @abstractmethod
    def get_description(self) -> str:
        pass

@dataclass
class Fish(FishableItem):
    species: str
    difficulty: FishDifficulty
    
    def __init__(self, name: str, species: str, rarity: float, weight: float, difficulty: FishDifficulty = FishDifficulty.MEDIUM):
        super().__init__(name, FishableType.FISH, rarity, weight)
        self.species = species
        self.difficulty = difficulty
    
    def get_description(self) -> str:
        return f"Caught a {self.name} ({self.species})!\nWeight: {self.weight:.2f}kg\nDifficulty: {self.difficulty.value.capitalize()}"

@dataclass
class TrashItem(FishableItem):
    def __init__(self, name: str, rarity: float, weight: float):
        super().__init__(name, FishableType.TRASH, rarity, weight)
    
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

def get_random_fishable() -> FishableItem:
    """Returns a random fishable item based on rarity"""
    # Increased chance to get fish vs trash
    if random.random() < 0.75:  # 75% chance to get a fish
        # Weighted selection based on rarity
        # Higher rarity value = more common
        total_rarity = sum(fish().rarity for fish in AVAILABLE_FISH)
        r = random.uniform(0, total_rarity)
        cumulative = 0
        
        for fish_gen in AVAILABLE_FISH:
            fish = fish_gen()
            cumulative += fish.rarity
            if r <= cumulative:
                return fish
                
        # Fallback in case of rounding errors
        return random.choice(AVAILABLE_FISH)()
    else:
        return random.choice(AVAILABLE_TRASH)() 