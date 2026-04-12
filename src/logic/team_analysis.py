import numpy as np
import pandas as pd
from ..utils.data_loader import get_type_chart

def analyze_defense(team):
    """Analyze team's defensive coverage."""
    type_chart = get_type_chart()
    defense_chart = type_chart["defense"]
    all_types = list(defense_chart.keys())
    
    # Initialize matrix with neutral effectiveness (1.0)
    defense_matrix = np.ones((len(team), len(all_types)))
    
    # Calculate effectiveness for each Pokémon against each type
    for i, pokemon in enumerate(team):
        for j, defend_type in enumerate(all_types):
            # Get effectiveness multiplier for this Pokémon's types
            mult = 1.0
            for poke_type in [pokemon['Type1'], pokemon['Type2']]:
                if poke_type and poke_type.strip() != " ":
                    if poke_type in defense_chart and defend_type in defense_chart[poke_type]:
                        mult *= defense_chart[poke_type][defend_type]
            defense_matrix[i, j] = mult
    
    # Calculate minimum effectiveness for each attacking type
    defense_summary = np.min(defense_matrix, axis=0)
    
    return defense_matrix, defense_summary, all_types

def analyze_attack(team):
    """Analyze team's offensive coverage."""
    type_chart = get_type_chart()
    attack_chart = type_chart["attack"]
    defend_types = list(attack_chart.keys())
    
    # Initialize matrices
    individual_attack = {}
    effectiveness_counts = {"super": 0, "neutral": 0, "resist": 0, "immune": 0}
    
    # Calculate each Pokémon's offensive coverage
    for pokemon in team:
        attack_types = [t for t in [pokemon['Type1'], pokemon['Type2']] if t and t.strip() != " "]
        effectiveness = {}
        
        for defend_type in defend_types:
            max_effectiveness = 1.0  # Start with neutral
            for attack_type in attack_types:
                if attack_type in attack_chart and defend_type in attack_chart[attack_type]:
                    max_effectiveness = max(max_effectiveness, attack_chart[attack_type][defend_type])
            
            effectiveness[defend_type] = max_effectiveness
        
        individual_attack[pokemon['Name']] = effectiveness
    
    # Calculate team's overall offensive coverage
    summary_matrix = {}
    for defend_type in defend_types:
        max_effectiveness = 0
        for pokemon_name, effectiveness in individual_attack.items():
            max_effectiveness = max(max_effectiveness, effectiveness.get(defend_type, 0))
        summary_matrix[defend_type] = max_effectiveness
        
        # Count effectiveness levels
        if max_effectiveness == 0:
            effectiveness_counts["immune"] += 1
        elif max_effectiveness < 1:
            effectiveness_counts["resist"] += 1
        elif max_effectiveness == 1:
            effectiveness_counts["neutral"] += 1
        else:
            effectiveness_counts["super"] += 1
    
    return individual_attack, summary_matrix, effectiveness_counts

def analyze_missing_types(team):
    """Analyze which types are missing from the team."""
    type_chart = get_type_chart()
    all_types = list(type_chart["defense"].keys())
    team_types = set()
    
    for pokemon in team:
        if pokemon['Type1'] and pokemon['Type1'].strip() != " ":
            team_types.add(pokemon['Type1'])
        if pokemon['Type2'] and pokemon['Type2'].strip() != " ":
            team_types.add(pokemon['Type2'])
    
    missing_types = [t for t in all_types if t not in team_types]
    return missing_types

def analyze_combined(team):
    """Combine defense, attack, and team-type presence into one analysis view model."""
    _, defense_summary, all_types = analyze_defense(team)
    _, attack_summary, _ = analyze_attack(team)
    team_type_set = set()

    for pokemon in team:
        for poke_type in [pokemon.get('Type1'), pokemon.get('Type2')]:
            if poke_type and poke_type.strip() != " ":
                team_type_set.add(poke_type)

    combined_rows = []
    for idx, type_name in enumerate(all_types):
        combined_rows.append({
            "type": type_name,
            "defense": float(defense_summary[idx]),
            "attack": float(attack_summary.get(type_name, 0.0)),
            "team_type_status": "Present" if type_name in team_type_set else "Missing"
        })

    return combined_rows

def analyze_team_profile(team, ignored_types=None):
    """Build weighted team profile for weaknesses, resistances, and offensive coverage."""
    ignored_types = ignored_types or set()
    type_chart = get_type_chart()
    defense_chart = type_chart["defense"]
    attack_chart = type_chart["attack"]
    all_types = list(defense_chart.keys())

    defense_rows = []
    resistance_rows = []
    coverage_rows = []

    for attack_type in all_types:
        if attack_type in ignored_types:
            continue

        defensive_values = []
        for pokemon in team:
            mult = 1.0
            for poke_type in [pokemon.get('Type1'), pokemon.get('Type2')]:
                if poke_type and str(poke_type).strip() != " ":
                    if poke_type in defense_chart and attack_type in defense_chart[poke_type]:
                        mult *= defense_chart[poke_type][attack_type]
            defensive_values.append(mult)

        weak_2x = sum(1 for v in defensive_values if np.isclose(v, 2.0))
        weak_4x = sum(1 for v in defensive_values if np.isclose(v, 4.0))
        resist_05 = sum(1 for v in defensive_values if np.isclose(v, 0.5))
        resist_025 = sum(1 for v in defensive_values if np.isclose(v, 0.25))
        immune_0 = sum(1 for v in defensive_values if np.isclose(v, 0.0))

        danger_score = (weak_2x + (3 * weak_4x)) - (resist_05 + (2 * resist_025) + (3 * immune_0))

        defensive_row = {
            "type": attack_type,
            "weak_2x": weak_2x,
            "weak_4x": weak_4x,
            "danger": danger_score,
        }
        resistance_row = {
            "type": attack_type,
            "resist_05": resist_05,
            "resist_025": resist_025,
            "immune_0": immune_0,
            "safety": resist_05 + (2 * resist_025) + (3 * immune_0),
        }

        defense_rows.append(defensive_row)
        resistance_rows.append(resistance_row)

        super_users = 0
        max_attack = 0.0
        for pokemon in team:
            poke_attack_types = [t for t in [pokemon.get('Type1'), pokemon.get('Type2')] if t and str(t).strip() != " "]
            best = 1.0
            for atk_type in poke_attack_types:
                if atk_type in attack_chart and attack_type in attack_chart[atk_type]:
                    best = max(best, attack_chart[atk_type][attack_type])
            if best > 1.0:
                super_users += 1
            max_attack = max(max_attack, best)

        coverage_rows.append({
            "type": attack_type,
            "super_users": super_users,
            "max_attack": max_attack,
        })

    weak_section = sorted(
        [row for row in defense_rows if (row["weak_2x"] + row["weak_4x"]) > 0],
        key=lambda row: (row["danger"], row["weak_4x"], row["weak_2x"]),
        reverse=True,
    )
    resist_section = sorted(
        [row for row in resistance_rows if (row["resist_05"] + row["resist_025"] + row["immune_0"]) > 0],
        key=lambda row: (row["safety"], row["immune_0"], row["resist_025"], row["resist_05"]),
        reverse=True,
    )
    coverage_section = sorted(
        coverage_rows,
        key=lambda row: (row["super_users"], row["max_attack"]),
        reverse=True,
    )

    return {
        "weaknesses": weak_section,
        "resistances": resist_section,
        "coverage": coverage_section,
    }