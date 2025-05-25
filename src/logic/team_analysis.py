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