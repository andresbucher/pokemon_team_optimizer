import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QListWidget, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..utils.image_handler import get_image_path
from ..logic.team_analysis import analyze_defense, analyze_team_profile, analyze_missing_types
from ..logic.suggestions import generate_team_suggestions

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
        self.display_pc_team_preview()
        self.display_pc_team_analysis()
    
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
        self.pc_team_layout.setContentsMargins(0, 0, 0, 0)
        self.pc_team_layout.setSpacing(8)
        self.pc_team_scroll.setWidget(self.pc_team_widget)
        
        # Controls for team building
        controls_layout = QHBoxLayout()
        self.build_team_button = QPushButton("Build Best Team")
        self.clear_team_button = QPushButton("Clear Team")
        controls_layout.addWidget(self.build_team_button)
        controls_layout.addWidget(self.clear_team_button)

        self.pc_team_status_label = QLabel("")
        self.pc_team_status_label.setStyleSheet("QLabel { font-size: 12px; color: #5B6470; }")

        analysis_label = QLabel("Built Team Analysis")
        analysis_label.setObjectName("subsection-title")
        self.pc_analysis_scroll = QScrollArea()
        self.pc_analysis_scroll.setWidgetResizable(True)
        self.pc_analysis_widget = QWidget()
        self.pc_analysis_layout = QVBoxLayout(self.pc_analysis_widget)
        self.pc_analysis_scroll.setWidget(self.pc_analysis_widget)
        
        # Add to team builder layout
        team_builder_layout.addWidget(self.pc_team_scroll)
        team_builder_layout.addLayout(controls_layout)
        team_builder_layout.addWidget(self.pc_team_status_label)
        team_builder_layout.addWidget(analysis_label)
        team_builder_layout.addWidget(self.pc_analysis_scroll)
        
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

    def get_pc_search_data(self):
        """Return data source for PC search (independent of Team Builder filters)."""
        return self.parent.pokemon_data
    
    def PC_Box_update_autofill(self):
        """Update PC box autofill suggestions based on search text."""
        query = self.PC_Box_search_entry.text().strip().lower()
        search_data = self.get_pc_search_data()
        
        if query:
            filtered_data = search_data[
                search_data.apply(
                    lambda row: self.matches_search_query(row, query),
                    axis=1
                )
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
        
        query = name.lower()
        search_data = self.get_pc_search_data()
        matches = search_data[
            search_data.apply(
                lambda row: self.matches_search_query(row, query),
                axis=1
            )
        ]
        if len(matches) == 0:
            return
        
        # Add first match to PC box
        pokemon = matches.iloc[0].to_dict()
        self.add_autofill_to_Box(pokemon)
        
        # Clear search
        self.PC_Box_search_entry.clear()
    
    def add_autofill_to_Box(self, pokemon_data):
        """Add Pokemon to the PC box."""
        pokemon_copy = dict(pokemon_data)
        pokemon_copy.setdefault('starred', False)

        # Add Pokémon to the PC-Box
        key = f"{pokemon_copy['Name']} {pokemon_copy['Form']}".strip()
        self.parent.pc_box[key] = pokemon_copy
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
            is_starred = bool(pokemon.get("starred", False))

            img_path = get_image_path(pokemon_id, name, form)

            pokemon_widget = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)

            top_row = QHBoxLayout()
            top_row.addStretch()
            remove_button = QPushButton("×")
            remove_button.setFixedSize(22, 22)
            remove_button.setStyleSheet(self.get_pc_box_control_style(is_starred=False))
            remove_button.clicked.connect(lambda _, k=key: self.remove_pc_box_pokemon(k))
            top_row.addWidget(remove_button)

            star_button = QPushButton("★" if is_starred else "☆")
            star_button.setFixedSize(22, 22)
            star_button.setStyleSheet(self.get_pc_box_control_style(is_starred=is_starred))
            star_button.clicked.connect(lambda _, k=key: self.toggle_pokemon_starred(k))
            top_row.addWidget(star_button)
            layout.addLayout(top_row)

            img_label = QLabel()
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(60, Qt.SmoothTransformation)
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("Image not found")
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label)

            form_text = f" ({form})" if form and form.strip() != "" and form.strip() != " " else ""
            name_label = QLabel(f"{name}{form_text}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("QLabel { font-size: 11px; }")
            layout.addWidget(name_label)

            layout.addWidget(self.build_compact_type_badges_widget(pokemon['Type1'], pokemon['Type2']))

            pokemon_widget.setLayout(layout)
            self.pc_box_layout.addWidget(pokemon_widget, idx // 8, idx % 8)

    def toggle_pokemon_starred(self, key):
        """Toggle starred status for a PC box Pokemon."""
        if key not in self.parent.pc_box:
            return

        current = bool(self.parent.pc_box[key].get("starred", False))
        self.parent.pc_box[key]["starred"] = not current
        self.display_pokemon_in_box()

    def get_pc_box_control_style(self, is_starred):
        """Return consistent styling for PC box control buttons."""
        return (
            "QPushButton {"
            f" border: 1px solid {'#C9A227' if is_starred else '#B8B8B8'};"
            " border-radius: 11px;"
            f" background-color: {'#FFF3C4' if is_starred else '#E9E9E9'};"
            f" color: {'#8A6D00' if is_starred else '#7A7A7A'};"
            " font-size: 12px;"
            " font-weight: bold;"
            " padding: 0px;"
            "}"
        )

    def remove_pc_box_pokemon(self, key):
        """Remove a Pokemon from the PC box and refresh all dependent views."""
        if key not in self.parent.pc_box:
            return

        self.parent.pc_box.pop(key, None)
        self.parent.pc_box_list = [existing_key for existing_key in self.parent.pc_box_list if existing_key != key]
        self.parent.team = [
            pokemon for pokemon in self.parent.team
            if f"{pokemon['Name']} {pokemon['Form']}".strip() != key
        ]

        self.display_pokemon_in_box()
        self.parent.team_builder_tab.display_team()
        self.display_pc_team_preview()
        self.display_pc_team_analysis()
        self.pc_team_status_label.setText("Removed Pokemon from PC Box.")

    def build_compact_type_badges_widget(self, type1, type2):
        """Create a compact row of colored type badges for PC box cards."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addStretch()

        if type1 and str(type1).strip() != "":
            layout.addWidget(self.create_compact_type_badge(str(type1).strip()))

        if type2 and str(type2).strip() != "":
            normalized_type2 = str(type2).strip()
            if normalized_type2 != " ":
                layout.addWidget(self.create_compact_type_badge(normalized_type2))

        layout.addStretch()
        return widget

    def create_compact_type_badge(self, type_name):
        """Create a smaller colored type badge for dense PC box layout."""
        badge_color = self.parent.type_colors.get(type_name, "#FFFFFF")
        text_color = self.get_contrasting_text_color(badge_color)
        badge = QLabel(type_name)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(58, 18)
        badge.setStyleSheet(
            "QLabel {"
            f" background-color: {badge_color};"
            " border: 1px solid #B9B9B9;"
            " border-radius: 9px;"
            " padding: 0px 4px;"
            f" color: {text_color};"
            " font-weight: bold;"
            " font-size: 9px;"
            "}"
        )
        return badge

    def get_contrasting_text_color(self, hex_color):
        """Return black or white text based on badge background luminance."""
        cleaned = hex_color.lstrip('#')
        if len(cleaned) != 6:
            return "#000000"

        try:
            red = int(cleaned[0:2], 16)
            green = int(cleaned[2:4], 16)
            blue = int(cleaned[4:6], 16)
        except ValueError:
            return "#000000"

        luminance = (0.299 * red) + (0.587 * green) + (0.114 * blue)
        return "#000000" if luminance > 160 else "#FFFFFF"

    def PC_Box_build_team(self):
        """Build a team from selected PC box Pokemon."""
        if not self.parent.pc_box_list:
            self.pc_team_status_label.setText("PC Box is empty. Add Pokemon first.")
            self.display_pc_team_preview()
            self.display_pc_team_analysis()
            return

        built_team, warning_message = self.build_best_team_from_box()
        self.parent.team = built_team

        # Update the team display in the team builder tab
        self.parent.team_builder_tab.display_team()
        self.display_pc_team_preview()
        self.display_pc_team_analysis()

        if warning_message:
            self.pc_team_status_label.setText(warning_message)
        else:
            self.pc_team_status_label.setText(f"Built best team with {len(self.parent.team)} Pokemon.")

    def PC_Box_clear_team(self):
        """Clear the current team being built."""
        self.parent.team = []
        self.parent.team_builder_tab.display_team()
        self.display_pc_team_preview()
        self.display_pc_team_analysis()
        self.pc_team_status_label.setText("Cleared current team.")

    def build_best_team_from_box(self):
        """Build the strongest team from PC box while honoring starred Pokemon locks."""
        ordered_candidates = [
            self.parent.pc_box[key]
            for key in self.parent.pc_box_list
            if key in self.parent.pc_box
        ]
        if not ordered_candidates:
            return [], "PC Box is empty."

        starred = [pokemon for pokemon in ordered_candidates if bool(pokemon.get("starred", False))]
        warning_message = ""
        if len(starred) > 6:
            starred = starred[:6]
            warning_message = "More than 6 starred Pokemon found. Using first 6 only."

        team = [dict(pokemon) for pokemon in starred]
        chosen_keys = {(pokemon['Name'], pokemon['Form']) for pokemon in team}

        remaining = [
            pokemon for pokemon in ordered_candidates
            if (pokemon['Name'], pokemon['Form']) not in chosen_keys
        ]

        while len(team) < 6 and remaining:
            remaining_df = pd.DataFrame([dict(pokemon) for pokemon in remaining])

            if team:
                effective_team = self.get_effective_team_for_generation(team)
                _, defense_summary, _ = analyze_defense(effective_team)
                ignored_types = {"Fairy"} if self.parent.team_builder_tab.is_pre_fairy_generation() else None

                suggestions = generate_team_suggestions(
                    effective_team,
                    remaining_df,
                    defense_summary,
                    ignored_types=ignored_types
                )

                if suggestions:
                    pick_name = suggestions[0]['name']
                    pick_form = suggestions[0]['form']
                    next_pick = next(
                        (
                            pokemon for pokemon in remaining
                            if pokemon['Name'] == pick_name and pokemon['Form'] == pick_form
                        ),
                        None,
                    )
                else:
                    next_pick = max(remaining, key=lambda pokemon: pokemon.get('Total', 0))
            else:
                next_pick = max(remaining, key=lambda pokemon: pokemon.get('Total', 0))

            if next_pick is None:
                break

            team.append(dict(next_pick))
            remaining = [
                pokemon for pokemon in remaining
                if not (pokemon['Name'] == next_pick['Name'] and pokemon['Form'] == next_pick['Form'])
            ]

        return team[:6], warning_message

    def get_effective_team_for_generation(self, team):
        """Apply pre-Gen-6 Fairy normalization for analysis-aware team building."""
        if not self.parent.team_builder_tab.is_pre_fairy_generation():
            return [dict(pokemon) for pokemon in team]

        normalized = []
        for pokemon in team:
            pokemon_copy = dict(pokemon)
            if pokemon_copy.get('Type1') == 'Fairy':
                pokemon_copy['Type1'] = 'Normal'
            if pokemon_copy.get('Type2') == 'Fairy':
                pokemon_copy['Type2'] = 'Normal'
            normalized.append(pokemon_copy)
        return normalized

    def display_pc_team_preview(self):
        """Render current team preview directly in PC tab."""
        while self.pc_team_layout.count():
            item = self.pc_team_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.parent.team:
            placeholder = QLabel("No team built yet.")
            placeholder.setStyleSheet("QLabel { color: #6B7280; font-size: 12px; }")
            self.pc_team_layout.addWidget(placeholder)
            self.pc_team_layout.addStretch()
            return

        for pokemon in self.parent.team:
            pokemon_widget = QWidget()
            layout = QVBoxLayout(pokemon_widget)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)

            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(get_image_path(pokemon["ID"], pokemon["Name"], pokemon["Form"]))
            if not pixmap.isNull():
                img_label.setPixmap(pixmap.scaledToWidth(52, Qt.SmoothTransformation))
            else:
                img_label.setText("No image")
            layout.addWidget(img_label)

            form = pokemon["Form"]
            form_text = f" ({form})" if form and str(form).strip() not in ["", " "] else ""
            name_label = QLabel(f"{pokemon['Name']}{form_text}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("QLabel { font-size: 10px; }")
            layout.addWidget(name_label)

            layout.addWidget(self.build_compact_type_badges_widget(pokemon['Type1'], pokemon['Type2']))
            self.pc_team_layout.addWidget(pokemon_widget)

        self.pc_team_layout.addStretch()

    def display_pc_team_analysis(self):
        """Render built-team analysis in PC tab using same design as Team Builder."""
        while self.pc_analysis_layout.count():
            item = self.pc_analysis_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.parent.team:
            label = QLabel("No team built yet.")
            self.pc_analysis_layout.addWidget(label)
            return

        effective_team = self.get_effective_team_for_generation(self.parent.team)
        ignored_types = {"Fairy"} if self.parent.team_builder_tab.is_pre_fairy_generation() else set()
        profile = analyze_team_profile(effective_team, ignored_types=ignored_types)

        weakness_by_type = {row["type"]: row for row in profile["weaknesses"]}
        resistance_by_type = {row["type"]: row for row in profile["resistances"]}
        matchup_types = sorted(set(weakness_by_type.keys()) | set(resistance_by_type.keys()))

        matchup_rows = []
        for type_name in matchup_types:
            weak_row = weakness_by_type.get(type_name, {"weak_2x": 0, "weak_4x": 0, "danger": 0})
            resist_row = resistance_by_type.get(type_name, {"resist_05": 0, "resist_025": 0, "immune_0": 0, "safety": 0})
            matchup_rows.append({
                "type": type_name,
                "weak_2x": weak_row["weak_2x"],
                "weak_4x": weak_row["weak_4x"],
                "danger": weak_row["danger"],
                "resist_05": resist_row["resist_05"],
                "resist_025": resist_row["resist_025"],
                "immune_0": resist_row["immune_0"],
                "safety": resist_row["safety"],
            })

        matchup_rows.sort(
            key=lambda row: (row["danger"], row["safety"], row["weak_4x"], row["immune_0"]),
            reverse=True,
        )

        missing_types = analyze_missing_types(effective_team)
        missing_types = [type_name for type_name in missing_types if type_name not in ignored_types]

        panel = QWidget()
        panel_layout = QHBoxLayout(panel)

        tb = self.parent.team_builder_tab
        panel_layout.addWidget(tb.build_matchups_card(matchup_rows, "#F4F8FC"))
        panel_layout.addWidget(tb.build_coverage_card(profile["coverage"], "#F6FBF4"))
        panel_layout.addWidget(tb.build_missing_types_grid_card(missing_types, "#FFF9F4"))

        self.pc_analysis_layout.addWidget(panel)

    def update_autofill(self):
        """Update PC box autofill suggestions without Team Builder filters."""
        # Get current search text
        query = self.PC_Box_search_entry.text().strip().lower()
        search_data = self.get_pc_search_data()
        
        if query:
            try:
                # Filter by name match
                filtered_data = search_data[
                    search_data.apply(
                        lambda row: self.matches_search_query(row, query),
                        axis=1
                    )
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
            
            # Find the exact match in full Pokemon data (filter-independent)
            search_data = self.get_pc_search_data()
            match = search_data[
                (search_data['Name'] == name) & 
                (search_data['Form'].fillna(' ') == form)
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

    def matches_search_query(self, row, query):
        """Match search against Pokemon name, form, and combined display text."""
        name = str(row.get('Name', '')).strip().lower()
        form = str(row.get('Form', '')).strip().lower()
        combined = f"{name} {form}".strip()

        return (
            query in name or
            (form and query in form) or
            query in combined
        )