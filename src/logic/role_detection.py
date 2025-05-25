def guess_role(pokemon):
    """Determine the role of a Pokemon based on its stats"""
    if pokemon['Speed'] >= 100 and pokemon['Attack'] >= 90 and pokemon['Sp. Atk'] >= 90:
        return 'Mixed Sweeper'
    if pokemon['Attack'] >= 90 and pokemon['Speed'] >= 90:
        return 'Physical Sweeper'
    if pokemon['Sp. Atk'] >= 90 and pokemon['Speed'] >= 90:
        return 'Special Sweeper'
    if pokemon['Defense'] >= 100 or (pokemon['Defense'] >= 80 and pokemon['HP'] >= 80):
        return 'Physical Wall'
    if pokemon['Sp. Def'] >= 100 or (pokemon['Sp. Def'] >= 80 and pokemon['HP'] >= 80):
        return 'Special Wall'
    return 'Generalist'

def identify_team_roles(team):
    """Identify roles for all Pokemon in a team"""
    return [guess_role(member) for member in team]