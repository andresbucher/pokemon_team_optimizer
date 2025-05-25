import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QListWidget, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..utils.image_handler import get_image_path

class PCWidgetTab(QWidget):
    """Tab for PC box Pokemon storage."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        
        # Create UI components
        self.create_search_section()
        self.create_pc_box_section()
        self.create_team_builder_section()
    
    def initialize_ui(self):
        """Initialize UI state and populate components."""
        # Setup connections
        self.setup_connections()
    
    def create_search_section(self):
        """Create search section for finding Pokemon."""
        search_layout = QHBoxLayout()
        
        # Search label and entry
        search_label = QLabel("Search Pokémon:")
        self.PC_Box_search_entry = QLineEdit()
        
        # Autofill results box
        self.PC_Box_autofill_box = QListWidget()
        self.PC_Box_autofill_box.setFixedHeight(0)  # Start hidden
        
        # Add Pokemon button
        self.PC_Box_add_pokemon_button = QPushButton("Add to PC Box")
        
        # Add to layout
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.PC_Box_search_entry)
        search_layout.addWidget(self.PC_Box_add_pokemon_button)
        
        # Add to main layout
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.PC_Box_autofill_box)
    
    def create_pc_box_section(self):
        """Create section to display PC box Pokemon."""
        # PC Box label
        pc_box_label = QLabel("PC Box")
        pc_box_label.setObjectName("section-title")
        
        # PC Box scroll area
        self.pc_box_scroll = QScrollArea()
        self.pc_box_scroll.setWidgetResizable(True)
        self.pc_box_widget = QWidget()
        self.pc_box_layout = QGridLayout(self.pc_box_widget)
        self.pc_box_scroll.setWidget(self.pc_box_widget)
        
        # Add to main layout
        self.layout.addWidget(pc_box_label)
        self.layout.addWidget(self.pc_box_scroll)
    
    def create_team_builder_section(self):
        """Create section for building team from PC box."""
        # Team builder label
        team_builder_label = QLabel("Build Team")
        team_builder_label.setObjectName("section-title")
        
        # Team builder area
        team_builder_layout = QVBoxLayout()
        
        # Current team display area
        self.pc_team_scroll = QScrollArea()
        self.pc_team_scroll.setWidgetResizable(True)
        self.pc_team_widget = QWidget()
        self.pc_team_layout = QHBoxLayout(self.pc_team_widget)
        self.pc_team_scroll.setWidget(self.pc_team_widget)
        
        # Controls for team building
        controls_layout = QHBoxLayout()
        self.build_team_button = QPushButton("Build Team")
        self.clear_team_button = QPushButton("Clear Team")
        controls_layout.addWidget(self.build_team_button)
        controls_layout.addWidget(self.clear_team_button)
        
        # Add to team builder layout
        team_builder_layout.addWidget(self.pc_team_scroll)
        team_builder_layout.addLayout(controls_layout)
        
        # Add to main layout
        self.layout.addWidget(team_builder_label)
        self.layout.addLayout(team_builder_layout)
    
    def setup_connections(self):
        """Set up signal connections for UI components."""
        # Connect search functionality
        self.PC_Box_search_entry.textChanged.connect(self.PC_Box_update_autofill)
        
        # Disconnect any existing connection first to avoid duplicates
        try:
            self.PC_Box_autofill_box.itemClicked.disconnect()
        except:
            pass
        
        # Connect autofill click directly to adding Pokémon
        self.PC_Box_autofill_box.itemClicked.connect(self.add_PC_Box_autofill_item)
        
        # Keep button for manual entry
        self.PC_Box_add_pokemon_button.clicked.connect(self.PC_Box_add_autofill)
        
        # Connect team builder buttons
        self.build_team_button.clicked.connect(self.PC_Box_build_team)
        self.clear_team_button.clicked.connect(self.PC_Box_clear_team)
    
    def PC_Box_update_autofill(self):
        """Update PC box autofill suggestions based on search text."""
        query = self.PC_Box_search_entry.text().strip().lower()
        
        if query:
            filtered_data = self.parent.filtered_data[
                self.parent.filtered_data['Name'].str.lower().str.contains(query)
            ].copy()
            self.PC_Box_populate_autofill_box(filtered_data.head(5))
        else:
            self.PC_Box_autofill_box.clear()
            self.PC_Box_autofill_box.setFixedHeight(0)
    
    def PC_Box_populate_autofill_box(self, filtered_data):
        """Populate the PC box autofill box with matching Pokemon."""
        self.PC_Box_autofill_box.clear()
        max_items = 5
        item_height = 30
        
        for _, pokemon in filtered_data.iterrows():
            form_text = f" ({pokemon['Form']})" if pokemon['Form'] != " " else ""
            item_text = f"{pokemon['Name']}{form_text}"
            self.PC_Box_autofill_box.addItem(item_text)
        
        # Adjust height to show items
        visible_count = min(len(filtered_data), max_items)
        self.PC_Box_autofill_box.setFixedHeight(visible_count * item_height if visible_count > 0 else 0)
    
    def select_PC_Box_autofill_item(self, item):
        """Handle PC box autofill item selection."""
        self.PC_Box_search_entry.setText(item.text().split(" (")[0])  # Set only the name part
        self.PC_Box_autofill_box.setFixedHeight(0)
    
    def PC_Box_add_autofill(self):
        """Add selected Pokemon to the PC box."""
        name = self.PC_Box_search_entry.text().strip()
        if not name:
            return
        
        # Find matching Pokemon
        matches = self.parent.filtered_data[self.parent.filtered_data['Name'] == name]
        if len(matches) == 0:
            return
        
        # Add first match to PC box
        pokemon = matches.iloc[0].to_dict()
        self.add_autofill_to_Box(pokemon)
        
        # Clear search
        self.PC_Box_search_entry.clear()
    
    def add_autofill_to_Box(self, pokemon_data):
        """Add Pokemon to the PC box."""
        # Add Pokémon to the PC-Box
        key = f"{pokemon_data['Name']} {pokemon_data['Form']}".strip()
        self.parent.pc_box[key] = pokemon_data
        self.parent.pc_box_list.append(key)
        self.display_pokemon_in_box()
    
    def display_pokemon_in_box(self):
        """Display the Pokemon in the PC box."""
        # Clear the current PC box layout
        for i in reversed(range(self.pc_box_layout.count())):
            widget = self.pc_box_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Display each Pokémon in the PC box
        for idx, key in enumerate(self.parent.pc_box_list):
            pokemon = self.parent.pc_box[key]
            pokemon_id = pokemon["ID"]
            name = pokemon["Name"]
            form = pokemon["Form"]

            img_path = get_image_path(pokemon_id, name, form)

            pokemon_widget = QWidget()
            layout = QVBoxLayout()

            img_label = QLabel()
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(80, Qt.SmoothTransformation)
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("Image not found")
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label)

            form_text = f" ({form})" if form and form.strip() != "" and form.strip() != " " else ""
            name_label = QLabel(f"{name}{form_text}")
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)

            pokemon_widget.setLayout(layout)
            self.pc_box_layout.addWidget(pokemon_widget, idx // 8, idx % 8)

    def PC_Box_build_team(self):
        """Build a team from selected PC box Pokemon."""
        # Example: Add the first 6 Pokémon from the PC box to the team
        self.parent.team = []
        for key in self.parent.pc_box_list[:6]:
            self.parent.team.append(self.parent.pc_box[key])
        # Update the team display in the team builder tab
        self.parent.team_builder_tab.display_team()

    def PC_Box_clear_team(self):
        """Clear the current team being built."""
        self.parent.team = []
        self.parent.team_builder_tab.display_team()

    def update_autofill(self):
        """Update PC box autofill suggestions based on current filters."""
        # Get current search text
        query = self.PC_Box_search_entry.text().strip().lower()
        
        if query:
            try:
                # Filter by name match
                filtered_data = self.parent.filtered_data[
                    self.parent.filtered_data['Name'].str.lower().str.contains(query)
                ].copy()
                
                # Sort results
                filtered_data = filtered_data.sort_values(by=['Name', 'Form'])
                
                # Populate autofill box
                self.PC_Box_populate_autofill_box(filtered_data.head(5))
            except Exception as e:
                print(f"Error updating PC box autofill: {str(e)}")
        else:
            # If search is empty, clear and hide autofill
            self.PC_Box_autofill_box.clear()
            self.PC_Box_autofill_box.setFixedHeight(0)

    def add_PC_Box_autofill_item(self, item):
        """Add the clicked autofill suggestion directly to the PC Box."""
        try:
            # Extract name and form from the item text
            text = item.text()
            print(f"Selected for PC Box: {text}")  # Debug print
            
            if " (" in text and text.endswith(")"):
                name, form = text.rsplit(" (", 1)
                form = form[:-1]  # remove trailing ')'
            else:
                name = text
                form = " "
            
            print(f"Looking for name='{name}', form='{form}'")
            
            # Find the exact match in filtered_data
            match = self.parent.filtered_data[
                (self.parent.filtered_data['Name'] == name) & 
                (self.parent.filtered_data['Form'].fillna(' ') == form)
            ]
            
            if len(match) == 0:
                print(f"No match found for {name} with form '{form}'")
                return
                
            # Add the Pokémon to the PC Box
            pokemon = match.iloc[0].to_dict()
            self.add_autofill_to_Box(pokemon)
            
            # Hide autofill box and clear search
            self.PC_Box_autofill_box.setFixedHeight(0)
            self.PC_Box_search_entry.clear()
            
        except Exception as e:
            import traceback
            print(f"Error in add_PC_Box_autofill_item: {str(e)}")
            traceback.print_exc()