import numpy as np
import pandas as pd
from .role_detection import guess_role
from .team_analysis import analyze_defense

def generate_team_suggestions(team, filtered_data, defense_summary):
    """Generate suggestions for team improvements."""
    suggestions = []
    
    # Skip if team is empty
    if not team:
        return suggestions
    
    # Get team's current types
    team_types = set()
    for pokemon in team:
        if pokemon['Type1'] and pokemon['Type1'].strip() != " ":
            team_types.add(pokemon['Type1'])
        if pokemon['Type2'] and pokemon['Type2'].strip() != " ":
            team_types.add(pokemon['Type2'])
    
    # Define weights for scoring
    weights = {
        "defense_improvement": 2.0,
        "new_type": 1.5,
        "stats": 1.0,
        "role_diversity": 1.0
    }
    
    # Get current team roles
    team_roles = [guess_role(pokemon) for pokemon in team]
    role_counts = {
        'Physical Sweeper': team_roles.count('Physical Sweeper'),
        'Special Sweeper': team_roles.count('Special Sweeper'),
        'Mixed Sweeper': team_roles.count('Mixed Sweeper'),
        'Physical Wall': team_roles.count('Physical Wall'),
        'Special Wall': team_roles.count('Special Wall'),
        'Generalist': team_roles.count('Generalist')
    }
    
    # Find weaknesses in current team
    weaknesses = []
    for i, value in enumerate(defense_summary):
        if value > 1.0:
            weaknesses.append(i)
    
    for _, pokemon in filtered_data.iterrows():
        # Skip Pokémon already in team
        if any(t['Name'] == pokemon['Name'] and t['Form'] == pokemon['Form'] for t in team):
            continue
        
        # Calculate defense improvement score
        defense_score = 0
        pokemon_dict = pokemon.to_dict()
        
        # Add to temporary team to evaluate defense
        temp_team = team.copy() + [pokemon_dict]
        _, new_defense_summary, all_types = analyze_defense(temp_team)
        
        # Check how much this Pokémon improves weaknesses
        for idx in weaknesses:
            old_value = defense_summary[idx]
            new_value = new_defense_summary[idx]
            if new_value < old_value:  # Lower is better for defense
                defense_score += (old_value - new_value) * 10  # Scale improvement
        
        # New type bonus
        new_type_bonus = 0
        poke_types = [t for t in [pokemon['Type1'], pokemon['Type2']] if t and t.strip() != " "]
        for t in poke_types:
            if t not in team_types:
                new_type_bonus += 5
        
        # Role diversity bonus
        role = guess_role(pokemon)
        role_diversity_bonus = 0
        if role_counts.get(role, 0) == 0:
            role_diversity_bonus += 10
        elif role_counts.get(role, 0) == 1:
            role_diversity_bonus += 5
        
        # Stats quality (baseline score from BST)
        stats_score = pokemon['Total'] / 100
        
        # Calculate final score
        total_score = (
            weights["defense_improvement"] * defense_score +
            weights["new_type"] * new_type_bonus +
            weights["stats"] * stats_score +
            weights["role_diversity"] * role_diversity_bonus
        )
        
        suggestions.append({
            'name': pokemon['Name'],
            'form': pokemon['Form'],
            'score': total_score,
            'role': role
        })
    
    # Sort suggestions by score in descending order
    sorted_suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)
    
    # Return top suggestions (e.g., top 18)
    return sorted_suggestions[:18]