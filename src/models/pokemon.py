class Pokemon:
    """Class representing a Pokemon with its attributes."""
    
    def __init__(self, data_row):
        """Initialize a Pokemon from a pandas DataFrame row."""
        self.id = str(data_row['ID'])
        self.name = data_row['Name']
        self.form = data_row['Form'] if not pd.isna(data_row['Form']) else " "
        self.type1 = data_row['Type1']
        self.type2 = data_row['Type2']
        self.hp = data_row['HP']
        self.attack = data_row['Attack']
        self.defense = data_row['Defense']
        self.sp_atk = data_row['Sp. Atk']
        self.sp_def = data_row['Sp. Def']
        self.speed = data_row['Speed']
        self.total = data_row['Total']
        self.generation = data_row['Generation']
    
    @property
    def key(self):
        """Unique key for this Pokemon."""
        form_text = f"-{self.form}" if self.form.strip() != " " else ""
        return f"{self.id}_{self.name}{form_text}"
    
    @property
    def display_name(self):
        """Display name including form if present."""
        form_text = f" ({self.form})" if self.form.strip() != " " else ""
        return f"{self.name}{form_text}"
    
    @property
    def types(self):
        """Returns a list of the Pokemon's types."""
        types = [self.type1]
        if self.type2 and self.type2.strip() != " ":
            types.append(self.type2)
        return types
    
    def to_dict(self):
        """Convert Pokemon to dictionary for team representation."""
        return {
            'ID': self.id,
            'Name': self.name,
            'Form': self.form,
            'Type1': self.type1,
            'Type2': self.type2,
            'HP': self.hp,
            'Attack': self.attack,
            'Defense': self.defense,
            'Sp. Atk': self.sp_atk,
            'Sp. Def': self.sp_def,
            'Speed': self.speed,
            'Total': self.total,
            'Generation': self.generation
        }


class TeamMember(Pokemon):
    """Extension of Pokemon with team-specific attributes."""
    
    def __init__(self, data_row):
        super().__init__(data_row)
        self.role = None  # Role will be set after analysis

    def set_role(self, role):
        """Set the role of this Pokemon in the team."""
        self.role = role