"""
tables.py
----------
This file just stores fixed reference data (like an Excel lookup table).
No type hints — just regular Python dictionaries and lists.
"""

# Main table of mushroom types and their growth parameters.
# Each mushroom name maps to another dictionary of its properties.
MUSHROOMS = {
    "Lion's Mane": {
        "incubation_days": 14,
        "cultural_inoculation_days": 21,
        "fruiting_days": 21,
        "expected_yield_ratio": 0.20,
        "default_grain_size_lbs": 3
    },
    "Turkey Tail": {
        "incubation_days": 21,
        "cultural_inoculation_days": 18,
        "fruiting_days": 30,
        "expected_yield_ratio": 0.15,
        "default_grain_size_lbs": 6
    },
    "Reishi": {
        "incubation_days": 45,
        "cultural_inoculation_days": 24,
        "fruiting_days": 75,
        "expected_yield_ratio": 0.16,
        "default_grain_size_lbs": 6
    },
    "Blue Oyster": {
        "incubation_days": 14,
        "cultural_inoculation_days": 21,
        "fruiting_days": 7,
        "expected_yield_ratio": 0.28,
        "default_grain_size_lbs": 3
    },
    "Pink Oyster": {
        "incubation_days": 14,
        "cultural_inoculation_days": 12,
        "fruiting_days": 8,
        "expected_yield_ratio": 0.24,
        "default_grain_size_lbs": 3
    },
    "King Oyster": {
        "incubation_days": 21,
        "cultural_inoculation_days": 18,
        "fruiting_days": 12,
        "expected_yield_ratio": 0.22,
        "default_grain_size_lbs": 3
    },
    "Yellow Oyster": {
        "incubation_days": 14,
        "cultural_inoculation_days": 12,
        "fruiting_days": 8,
        "expected_yield_ratio": 0.11,
        "default_grain_size_lbs": 3
    },
    "Pearl Oyster": {
        "incubation_days": 21,
        "cultural_inoculation_days": 14,
        "fruiting_days": 6,
        "expected_yield_ratio": 0.28,
        "default_grain_size_lbs": 3
    },
    "Shiitake": {
        "incubation_days": 56,
        "cultural_inoculation_days": 70,
        "fruiting_days": 75,
        "expected_yield_ratio": 0.28,
        "default_grain_size_lbs": 6
    },
    "Pioppino": {
        "incubation_days": 21,
        "cultural_inoculation_days": 30,
        "fruiting_days": 10,
        "expected_yield_ratio": 0.32,
        "default_grain_size_lbs": 3
    }
}

# Lists for dropdown menus in Streamlit
MUSHROOM_LIST = list(MUSHROOMS.keys())
FRUITING_BAG_SIZES_LBS = [5, 10]
SUBSTRATE_TYPES = ["Masters Mix", "Chopped Straw", "Saw Dust"]

# Sterilizer capacity depends on bag size (used in cycle calculation)
STERILIZER_CAPACITY_PER_CYCLE = {
    5: 40,
    10: 20
}

# Mix ratios (per 1 lb of substrate bag)
SUBSTRATE_MIX_RATIOS = {
    "hw_pellets_per_lb": 0.20,
    "sh_pellets_per_lb": 0.20,
    "water_per_lb": 0.60
}

# Small buffer to cover losses
LOSS_FACTOR = 1.02
