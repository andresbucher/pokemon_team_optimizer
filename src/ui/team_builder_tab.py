import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QLineEdit, QListWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..utils.image_handler import get_image_path
from ..logic.team_analysis import analyze_defense, analyze_attack, analyze_missing_types
from ..logic.suggestions import generate_team_suggestions

class TeamBuilderTab(QWidget):
    """Tab for building and analyzing Pokemon teams."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self.create_filters_section()
        self.create_search_section()
        self.create_team_display_section()
        self.create_analysis_section()
        self.create_suggestions_section()
    
    def initialize_ui(self):
        """Initialize UI state and populate components."""
        # Populate filter options
        self.populate_type_filter()
        self.populate_generation_filter()
        
        # Set up initial connections
        self.setup_connections()
    
    def create_filters_section(self):
        """Create filters for Pokemon selection."""
        filters_layout = QHBoxLayout()
        
        # Generation filter
        gen_label = QLabel("Generation:")
        self.gen_filter = QComboBox()
        self.gen_filter.addItem("All Generations")
        
        # Type filter
        type_label = QLabel("Type:")
        self.type_filter = QComboBox()
        
        # Mega evolution filter
        self.mega_filter = QCheckBox("Include Mega/Special Forms")
        self.mega_filter.setChecked(True)
        
        # Legendary filter
        self.legendary_filter = QCheckBox("Include Legendary Pokémon")
        self.legendary_filter.setChecked(True)
        
        # Add to layout
        filters_layout.addWidget(gen_label)
        filters_layout.addWidget(self.gen_filter)
        filters_layout.addWidget(type_label)
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(self.mega_filter)
        filters_layout.addWidget(self.legendary_filter)
        
        # Add apply filters button
        self.apply_filters_button = QPushButton("Apply Filters")
        filters_layout.addWidget(self.apply_filters_button)
        
        # Add to main layout
        self.layout.addLayout(filters_layout)
    
    def create_search_section(self):
        """Create search section for finding Pokemon."""
        search_layout = QHBoxLayout()
        
        # Search label and entry
        search_label = QLabel("Search Pokémon:")
        self.search_entry = QLineEdit()
        
        # Autofill results box
        self.autofill_box = QListWidget()
        self.autofill_box.setFixedHeight(0)  # Start hidden
        
        # Add Pokemon button
        self.add_pokemon_button = QPushButton("Add to Team")
        
        # Add to layout
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(self.add_pokemon_button)
        
        # Add to main layout
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.autofill_box)
    
    def create_team_display_section(self):
        """Create section to display the current team."""
        # Team scroll area
        team_scroll = QScrollArea()
        team_scroll.setWidgetResizable(True)
        team_widget = QWidget()
        self.team_layout = QHBoxLayout(team_widget)
        team_scroll.setWidget(team_widget)
        
        # Add to main layout
        team_label = QLabel("Current Team:")
        team_label.setObjectName("section-title")
        self.layout.addWidget(team_label)
        self.layout.addWidget(team_scroll)
    
    def create_analysis_section(self):
        """Create section for team analysis."""
        # Analysis label
        analysis_label = QLabel("Team Analysis")
        analysis_label.setObjectName("section-title")
        
        # Analysis buttons
        analysis_buttons_layout = QHBoxLayout()
        self.analyze_defense_button = QPushButton("Analyze Defense")
        self.analyze_attack_button = QPushButton("Analyze Attack")
        self.analyze_missing_types_button = QPushButton("Analyze Missing Types")
        self.clear_analysis_button = QPushButton("Clear Analysis")
        
        analysis_buttons_layout.addWidget(self.analyze_defense_button)
        analysis_buttons_layout.addWidget(self.analyze_attack_button)
        analysis_buttons_layout.addWidget(self.analyze_missing_types_button)
        analysis_buttons_layout.addWidget(self.clear_analysis_button)
        
        # Analysis results area
        self.analysis_scroll = QScrollArea()
        self.analysis_scroll.setWidgetResizable(True)
        self.analysis_widget = QWidget()
        self.analysis_layout = QVBoxLayout(self.analysis_widget)
        self.analysis_scroll.setWidget(self.analysis_widget)
        
        # Add to main layout
        self.layout.addWidget(analysis_label)
        self.layout.addLayout(analysis_buttons_layout)
        self.layout.addWidget(self.analysis_scroll)
    
    def create_suggestions_section(self):
        """Create section for team suggestions."""
        # Suggestions label
        suggestions_label = QLabel("Team Suggestions")
        suggestions_label.setObjectName("section-title")
        
        # Generate suggestions button
        self.generate_suggestions_button = QPushButton("Generate Suggestions")
        
        # Suggestions display area
        self.suggestions_scroll = QScrollArea()
        self.suggestions_scroll.setWidgetResizable(True)
        self.suggestions_widget = QWidget()
        self.suggestions_layout = QGridLayout(self.suggestions_widget)
        self.suggestions_scroll.setWidget(self.suggestions_widget)
        
        # Add to main layout
        self.layout.addWidget(suggestions_label)
        self.layout.addWidget(self.generate_suggestions_button)
        self.layout.addWidget(self.suggestions_scroll)
    
    def populate_type_filter(self):
        """Populate type filter with Pokemon types."""
        self.type_filter.clear()
        self.type_filter.addItem("All Types")
        
        types = sorted(self.parent.pokemon_data['Type1'].unique())
        for type_name in types:
            self.type_filter.addItem(type_name)
    
    def populate_generation_filter(self):
        """Populate generation filter with available generations."""
        self.gen_filter.clear()
        self.gen_filter.addItem("All Generations")
        
        max_gen = self.parent.pokemon_data['Generation'].max()
        for gen in range(1, max_gen + 1):
            self.gen_filter.addItem(f"Gen {gen}")
    
    def setup_connections(self):
        """Set up signal connections for UI components."""
        # Connect filter components
        self.apply_filters_button.clicked.connect(self.parent.apply_filters)
        
        # Connect search functionality
        self.search_entry.textChanged.connect(self.update_autofill)
        
        # Disconnect any existing connection first to avoid duplicates
        try:
            self.autofill_box.itemClicked.disconnect()
        except:
            pass
        
        # Connect the click handler directly to team addition
        self.autofill_box.itemClicked.connect(self.add_autofill_item_to_team)
        
        # Keep the Add button for manual entry
        self.add_pokemon_button.clicked.connect(self.add_autofill_to_team)
        
        # Connect analysis buttons
        self.analyze_defense_button.clicked.connect(self.analyze_defense)
        self.analyze_attack_button.clicked.connect(self.analyze_attack)
        self.analyze_missing_types_button.clicked.connect(self.analyze_missing_types)
        self.clear_analysis_button.clicked.connect(self.clear_analysis)
        
        # Connect suggestions button
        self.generate_suggestions_button.clicked.connect(self.generate_suggestions)
    
    def update_autofill(self):
        """Update autofill suggestions based on search text."""
        query = self.search_entry.text().strip().lower()
        
        if query:
            try:
                filtered_data = self.parent.filtered_data[
                    self.parent.filtered_data['Name'].str.lower().str.contains(query)
                ].copy()

                # Sort by name for consistent results
                filtered_data = filtered_data.sort_values(by=['Name', 'Form'])

                # If the search query is empty, show all results
                if filtered_data.empty:
                    self.autofill_box.clear()
                    self.autofill_box.setFixedHeight(0)
                    return
                
                # Populate the autofill box with the top 5 results
                self.populate_autofill_box(filtered_data.head(5))
            except Exception as e:
                print(f"Error in PC_Box update_autofill: {str(e)}")
        else:
            self.autofill_box.clear()
            self.autofill_box.setFixedHeight(0)
    
    def populate_autofill_box(self, filtered_data):
        self.autofill_box.clear()
        max_items = 5
        item_height = 30

        for _, pokemon in filtered_data.iterrows():
            form_text = f" ({pokemon['Form']})" if pokemon['Form'] != " " else ""
            item_text = f"{pokemon['Name']}{form_text}"
            self.autofill_box.addItem(item_text)

        visible_count = min(len(filtered_data), max_items)
        self.autofill_box.setFixedHeight(visible_count * item_height if visible_count > 0 else 0)

    def select_autofill_item(self, item):
        """Handle autofill item selection."""
        self.search_entry.setText(item.text().split(" (")[0])  # Set only the name part
        self.autofill_box.setFixedHeight(0)
    
    def add_autofill_to_team(self):
        """Add selected Pokemon to the team."""
        if len(self.parent.team) >= 6:
            return  # Team is full
        
        name = self.search_entry.text().strip()
        if not name:
            return
        
        # Find matching Pokemon
        matches = self.parent.filtered_data[self.parent.filtered_data['Name'] == name]
        if len(matches) == 0:
            return
        
        # Add first match to team
        pokemon = matches.iloc[0].to_dict()
        self.parent.team.append(pokemon)
        
        # Clear search and display updated team
        self.search_entry.clear()
        self.display_team()
    
    def display_team(self):
        """Display the current team."""
        # Clear the current team layout
        for i in reversed(range(self.team_layout.count())):
            widget = self.team_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Display each Pokémon in the team
        for pokemon in self.parent.team:
            pokemon_id = pokemon["ID"]
            name = pokemon["Name"]
            form = pokemon["Form"]

            img_path = get_image_path(pokemon_id, name, form)

            pokemon_widget = QWidget()
            layout = QVBoxLayout()

            img_label = QLabel()
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("Image not found")
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label)

            # Name and Form
            form_text = f" ({form})" if form and form.strip() != "" and form.strip() != " " else ""
            name_label = QLabel(f"{name}{form_text}")
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)

            # Types
            types = f"{pokemon['Type1']}/{pokemon['Type2']}" if pokemon["Type2"] != " " else pokemon['Type1']
            types_label = QLabel(types)
            types_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(types_label)

            pokemon_widget.setLayout(layout)
            self.team_layout.addWidget(pokemon_widget)

    def analyze_defense(self):
        """Analyze team's defensive capabilities."""
        self.clear_analysis()
        if not self.parent.team:
            label = QLabel("No team members to analyze.")
            self.analysis_layout.addWidget(label)
            return

        _, defense_summary, all_types = analyze_defense(self.parent.team)
        result = "Defense Summary:\n"
        for t, val in zip(all_types, defense_summary):
            result += f"{t}: {val}\n"
        label = QLabel(result)
        self.analysis_layout.addWidget(label)

    def analyze_attack(self):
        """Analyze team's offensive capabilities."""
        self.clear_analysis()
        if not self.parent.team:
            label = QLabel("No team members to analyze.")
            self.analysis_layout.addWidget(label)
            return

        _, summary_matrix, effectiveness_counts = analyze_attack(self.parent.team)
        result = "Attack Summary:\n"
        for t, val in summary_matrix.items():
            result += f"{t}: {val}\n"
        label = QLabel(result)
        self.analysis_layout.addWidget(label)

    def analyze_missing_types(self):
        """Analyze types missing from the team."""
        self.clear_analysis()
        if not self.parent.team:
            label = QLabel("No team members to analyze.")
            self.analysis_layout.addWidget(label)
            return

        missing_types = analyze_missing_types(self.parent.team)
        result = "Missing Types:\n" + ", ".join(missing_types)
        label = QLabel(result)
        self.analysis_layout.addWidget(label)

    def clear_analysis(self):
        """Clear analysis results."""
        while self.analysis_layout.count():
            item = self.analysis_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def generate_suggestions(self):
        """Generate team improvement suggestions."""
        if not self.parent.team:
            self.display_suggestions([])
            return
        _, defense_summary, _ = analyze_defense(self.parent.team)
        suggestions = generate_team_suggestions(self.parent.team, self.parent.filtered_data, defense_summary)
        self.display_suggestions(suggestions)

    def display_suggestions(self, suggestions):
        """Display the generated suggestions."""
        # Clear previous suggestions
        while self.suggestions_layout.count():
            item = self.suggestions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        fixed_width = 100
        for i, suggestion in enumerate(suggestions):
            name = suggestion['name']
            form = suggestion['form']
            score = round(suggestion['score'], 2)
            role = suggestion['role']

            pokemon = self.parent.pokemon_data[
                (self.parent.pokemon_data['Name'] == name) & (self.parent.pokemon_data['Form'] == form)
            ].iloc[0]
            types = f"{pokemon['Type1']}/{pokemon['Type2']}" if pokemon["Type2"] != " " else pokemon['Type1']
            bst_total = pokemon['Total']
            form_text = f" ({form})" if form != " " else ""
            image_path = get_image_path(pokemon['ID'], name, form)

            suggestion_label = QLabel(
                f"Name: {name}{form_text}\nTypes: {types}\nBST: {bst_total}\nRole: {role}\nScore: {score}"
            )

            image_label = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(fixed_width, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image not found")

            vbox = QVBoxLayout()
            vbox.addWidget(image_label)
            vbox.addWidget(suggestion_label)
            widget = QWidget()
            widget.setLayout(vbox)
            self.suggestions_layout.addWidget(widget, i // 6, i % 6)

    def add_autofill_item_to_team(self, item):
        """Add the clicked autofill suggestion directly to the team."""
        try:
            # The item text should be "Name (Form)" or just "Name"
            text = item.text()
            print(f"Selected: {text}")  # Debug print
            
            if " (" in text and text.endswith(")"):
                name, form = text.rsplit(" (", 1)
                form = form[:-1]  # remove trailing ')'
            else:
                name = text
                form = " "
            
            print(f"Looking for name='{name}', form='{form}'")  # Debug print
            
            # Find the exact match in filtered_data
            match = self.parent.filtered_data[
                (self.parent.filtered_data['Name'] == name) & 
                (self.parent.filtered_data['Form'].fillna(' ') == form)
            ]
            
            if len(match) == 0:
                print(f"No match found for {name} with form '{form}'")
                return
                
            pokemon = match.iloc[0].to_dict()
            if len(self.parent.team) < 6:
                self.parent.team.append(pokemon)
                self.display_team()
            
            # Hide autofill box and clear search
            self.autofill_box.setFixedHeight(0)
            self.search_entry.clear()
            
        except Exception as e:
            import traceback
            print(f"Error in add_autofill_item_to_team: {str(e)}")
            traceback.print_exc()