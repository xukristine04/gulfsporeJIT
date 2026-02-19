"""
planner.py
-----------
This file performs all calculations (the logic behind the spreadsheet).
It takes the user’s “desired yield” and “desired harvest date” and works backward.
"""

import math
from datetime import timedelta
from tables import MUSHROOMS, STERILIZER_CAPACITY_PER_CYCLE, SUBSTRATE_MIX_RATIOS, LOSS_FACTOR

def compute_plan(
    desired_yield_lbs,
    desired_harvest_date,
    fruiting_bag_size_lbs,
    mushroom_row,
    substrate_type,
    spawn_purchased,
    sub_bags_duration_days=1.0,
    sub_ster_duration_days=3.0,
    num_sterilizers=2,
    gsi_bag_size_lbs=None,
    gbs_duration_days=1.0
):
    # ---------------------------
    # 1. Fruiting (anchor step)
    # ---------------------------
    exp_ratio = mushroom_row["expected_yield_ratio"]
    fruit_days = mushroom_row["fruiting_days"]

    # number of bags needed to reach desired yield
    fruit_num_bags = math.ceil((desired_yield_lbs * LOSS_FACTOR) / (exp_ratio * fruiting_bag_size_lbs))

    fruit_end = desired_harvest_date
    fruit_start = desired_harvest_date - timedelta(days=fruit_days)

    fruiting = {
        "name": "Fruiting",
        "date_start": fruit_start,
        "date_end": fruit_end,
        "duration_days": fruit_days,
        "bag_size": fruiting_bag_size_lbs,
        "num_bags": fruit_num_bags,
        "expected_yield_ratio": exp_ratio
    }

    # ---------------------------
    # 2. Substrate Bag Incubation
    # ---------------------------
    sub_incub_days = mushroom_row["incubation_days"]
    sub_inc_end = fruit_start
    sub_inc_start = sub_inc_end - timedelta(days=sub_incub_days)
    sub_inc_bags = math.ceil(fruit_num_bags * LOSS_FACTOR)

    substrate_incub = {
        "name": "Substrate Bags Incubation",
        "date_start": sub_inc_start,
        "date_end": sub_inc_end,
        "duration_days": sub_incub_days,
        "bag_size": fruiting_bag_size_lbs,
        "num_bags": sub_inc_bags,
        "substrate_type": substrate_type
    }

    # ---------------------------
    # 3. Grain Spawn Incubation
    # ---------------------------
    if gsi_bag_size_lbs is None:
        gsi_bag_size_lbs = mushroom_row["default_grain_size_lbs"]

    if spawn_purchased:
        gsi_duration = 1
    else:
        gsi_duration = mushroom_row["cultural_inoculation_days"] + 1

    gsi_end = sub_inc_start
    gsi_start = gsi_end - timedelta(days=gsi_duration)

    gsi = {
        "name": "Grain Spawn Incubation",
        "date_start": gsi_start,
        "date_end": gsi_end,
        "duration_days": gsi_duration,
        "bag_size": gsi_bag_size_lbs,
        "spawn_purchased": spawn_purchased
    }

    # ---------------------------
    # 4. Substrate Bag Sterilization
    # ---------------------------
    sub_ster_end = gsi["date_start"]
    sub_ster_start = sub_ster_end - timedelta(days=sub_ster_duration_days)

    capacity = STERILIZER_CAPACITY_PER_CYCLE[fruiting_bag_size_lbs]
    sub_ster_bags = math.ceil(sub_inc_bags * LOSS_FACTOR)
    cycles = math.ceil(sub_ster_bags / (capacity * num_sterilizers))

    substrate_ster = {
        "name": "Substrate Bags Sterilization",
        "date_start": sub_ster_start,
        "date_end": sub_ster_end,
        "duration_days": sub_ster_duration_days,
        "num_bags": sub_ster_bags,
        "bag_size": fruiting_bag_size_lbs,
        "num_sterilizers": num_sterilizers,
        "capacity_per_cycle": capacity,
        "cycles": cycles
    }

    # ---------------------------
    # 5. Substrate Bag Mixing
    # ---------------------------
    sub_bags_end = sub_ster_start
    sub_bags_start = sub_bags_end - timedelta(days=sub_bags_duration_days)

    hw_per_bag = SUBSTRATE_MIX_RATIOS["hw_pellets_per_lb"] * fruiting_bag_size_lbs
    sh_per_bag = SUBSTRATE_MIX_RATIOS["sh_pellets_per_lb"] * fruiting_bag_size_lbs
    water_per_bag = SUBSTRATE_MIX_RATIOS["water_per_lb"] * fruiting_bag_size_lbs

    substrate_bags = {
        "name": "Substrate Bags (Mixing)",
        "date_start": sub_bags_start,
        "date_end": sub_bags_end,
        "duration_days": sub_bags_duration_days,
        "num_bags": sub_ster_bags,
        "hw_per_bag": hw_per_bag,
        "sh_per_bag": sh_per_bag,
        "water_per_bag": water_per_bag
    }

    # ---------------------------
    # 6. Grain Bag Sterilization
    # ---------------------------
    gbs_end = sub_ster_start
    gbs_start = gbs_end - timedelta(days=gbs_duration_days)

    grain_bag_ster = {
        "name": "Grain Bags Sterilization",
        "date_start": gbs_start,
        "date_end": gbs_end,
        "duration_days": gbs_duration_days
    }

    # ---------------------------
    # 7. Grain Bag Mixing
    # ---------------------------
    gb_end = gbs_start
    # OLD: gb_start = gb_end - timedelta(days=0.5)
    # NEW (explicit 12 hours):
    gb_start = gb_end - timedelta(days=1) #show previous calendar day

    grain_bags = {
        "name": "Grain Bags (Mixing)",
        "date_start": gb_start,
        "date_end": gb_end,
        "duration_days": 0.5
    }

    # ---------------------------
    # Create full plan output
    # ---------------------------
    blocks = [grain_bags, grain_bag_ster, substrate_bags, substrate_ster, gsi, substrate_incub, fruiting]

    # ✅ NEW: Find the earliest starting date across all workflow blocks
    earliest_start = min(b["date_start"] for b in blocks)

    #new computation
    logical_earliest = earliest_start
    try:
        # If the first block is Grain Bags (0.5 day) and we purposely showed it on the
        # prior calendar day, add 1 day back for *duration math* so we don't overcount
        if earliest_start == grain_bags["date_start"] and grain_bags.get("duration_days") == 0.5:
            logical_earliest = earliest_start + timedelta(days=1)
    except NameError:
        # If grain_bags isn't in scope for some reason, just fall back to earliest_start
        pass

    total_days = (fruit_end - logical_earliest).days
    weeks, days = divmod(total_days, 7)

    # --- MIX RATIOS (per bag) ---
    mix_ratio = [
        {
            "Component": "HW pellets (lbs per bag)",
            "Amount (lbs)": hw_per_bag,
        },
        {
            "Component": "SH pellets (lbs per bag)",
            "Amount (lbs)": sh_per_bag,
        },
        {
            "Component": "Water (lbs per bag)",
            "Amount (lbs)": water_per_bag,
        },
    ]

    # --- MATERIAL TOTALS (for sterilization batch) ---
    materials = [
        {
            "Material": "HW pellets total (lbs)",
            "Total": hw_per_bag * sub_ster_bags,
        },
        {
            "Material": "SH pellets total (lbs)",
            "Total": sh_per_bag * sub_ster_bags,
        },
        {
            "Material": "Water total (lbs)",
            "Total": water_per_bag * sub_ster_bags,
        },
        {
            "Material": "Bags planned",
            "Total": sub_ster_bags,
        },
        {
            "Material": "Bag size (lbs)",
            "Total": fruiting_bag_size_lbs,
        },
    ]

    # ✅ NEW: summary using earliest start instead of substrate_bags["date_start"]
    summary = {
        "Fruiting bags": fruit_num_bags,
        "Schedule starts": earliest_start,
        "Schedule ends": fruit_end,
        "Total duration": f"{weeks} weeks, {days} days"
    }

    return {
    "blocks": blocks,
    "mix_ratio": mix_ratio,
    "materials": materials,
    "summary": summary,
}
