import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QLineEdit, QListWidget, QScrollArea,
    QSizePolicy, QGridLayout, QFrame
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..utils.image_handler import get_image_path
from ..logic.team_analysis import analyze_defense, analyze_team_profile, analyze_missing_types
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

        self.filters_note_label = QLabel("Note: Gen Filters affect analysis and suggestions, but not search results (Fairy Type)")
        self.filters_note_label.setStyleSheet("QLabel { font-size: 12px; color: #5B6470; }")
        self.layout.addWidget(self.filters_note_label)
    
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
        # Team display area (non-scrollable)
        team_widget = QWidget()
        self.team_layout = QHBoxLayout(team_widget)
        self.team_layout.setContentsMargins(0, 0, 0, 0)
        self.team_layout.setSpacing(8)
        self.team_layout.addStretch()
        
        # Add to main layout
        team_label = QLabel("Current Team:")
        team_label.setObjectName("section-title")
        self.layout.addWidget(team_label)
        self.layout.addWidget(team_widget)
    
    def create_analysis_section(self):
        """Create section for team analysis."""
        # Analysis label
        analysis_label = QLabel("Team Analysis")
        analysis_label.setObjectName("section-title")
        
        # Analysis buttons
        analysis_buttons_layout = QHBoxLayout()
        self.analyze_team_button = QPushButton("Analyze Team (Defense + Attack + Types)")
        self.clear_analysis_button = QPushButton("Clear Analysis")
        self.generate_suggestions_button = QPushButton("Generate Suggestions")
        
        analysis_buttons_layout.addWidget(self.analyze_team_button)
        analysis_buttons_layout.addWidget(self.clear_analysis_button)
        analysis_buttons_layout.addWidget(self.generate_suggestions_button)
        
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
        
        # Suggestions display area
        self.suggestions_scroll = QScrollArea()
        self.suggestions_scroll.setWidgetResizable(True)
        self.suggestions_widget = QWidget()
        self.suggestions_layout = QGridLayout(self.suggestions_widget)
        self.suggestions_layout.setContentsMargins(6, 6, 6, 6)
        self.suggestions_layout.setHorizontalSpacing(8)
        self.suggestions_layout.setVerticalSpacing(8)
        self.suggestions_scroll.setWidget(self.suggestions_widget)
        
        # Add to main layout
        self.layout.addWidget(suggestions_label)
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
        self.analyze_team_button.clicked.connect(self.analyze_team)
        self.clear_analysis_button.clicked.connect(self.clear_analysis)
        
        # Connect suggestions button
        self.generate_suggestions_button.clicked.connect(self.generate_suggestions)
    
    def update_autofill(self):
        """Update autofill suggestions based on search text."""
        query = self.search_entry.text().strip().lower()
        
        if query:
            try:
                filtered_data = self.parent.filtered_data[
                    self.parent.filtered_data.apply(
                        lambda row: self.matches_search_query(row, query),
                        axis=1
                    )
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
        
        name_query = name.lower()
        matches = self.parent.filtered_data[
            self.parent.filtered_data.apply(
                lambda row: self.matches_search_query(row, name_query),
                axis=1
            )
        ]
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
        while self.team_layout.count():
            item = self.team_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Display each Pokemon in the team
        for index, pokemon in enumerate(self.parent.team):
            pokemon_id = pokemon["ID"]
            name = pokemon["Name"]
            form = pokemon["Form"]

            img_path = get_image_path(pokemon_id, name, form)

            pokemon_widget = QWidget()
            layout = QVBoxLayout()

            remove_row = QHBoxLayout()
            remove_row.addStretch()
            remove_button = QPushButton("x")
            remove_button.setObjectName("remove-card-button")
            remove_button.setFixedSize(24, 24)
            remove_button.setCursor(Qt.PointingHandCursor)
            remove_button.clicked.connect(lambda _, idx=index: self.remove_team_member(idx))
            remove_row.addWidget(remove_button)
            layout.addLayout(remove_row)

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
            type_widget = self.build_type_badges_widget(pokemon['Type1'], pokemon['Type2'])
            layout.addWidget(type_widget)

            pokemon_widget.setLayout(layout)
            self.team_layout.addWidget(pokemon_widget)

        self.team_layout.addStretch()

    def matches_search_query(self, row, query):
        """Match search against Pokemon name/form with order-independent tokens."""
        normalized_query = self.normalize_search_text(query)
        if not normalized_query:
            return True

        name = self.normalize_search_text(str(row.get('Name', '')))
        form = self.normalize_search_text(str(row.get('Form', '')))
        combined = f"{name} {form}".strip()

        if normalized_query in combined:
            return True

        query_tokens = normalized_query.split()
        return all(token in combined for token in query_tokens)

    def normalize_search_text(self, text):
        """Normalize text for robust search matching."""
        normalized = str(text).lower().strip()
        for char in ["(", ")", "-", "_", "/", ","]:
            normalized = normalized.replace(char, " ")
        return " ".join(normalized.split())

    def build_type_badges_widget(self, type1, type2):
        """Create a centered row of colored type badges."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addStretch()

        if type1 and str(type1).strip() != "":
            layout.addWidget(self.create_type_badge(str(type1).strip()))
        if type2 and str(type2).strip() != "":
            normalized_type2 = str(type2).strip()
            if normalized_type2 != " ":
                layout.addWidget(self.create_type_badge(normalized_type2))

        layout.addStretch()
        return widget

    def create_type_badge(self, type_name):
        """Create a single type badge with consistent colors and contrast."""
        badge_color = self.parent.type_colors.get(type_name, "#FFFFFF")
        text_color = self.get_contrasting_text_color(badge_color)
        badge = QLabel(type_name)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(72, 24)
        badge.setStyleSheet(
            "QLabel {"
            f" background-color: {badge_color};"
            " border: 1px solid #B9B9B9;"
            " border-radius: 11px;"
            " padding: 0px 6px;"
            f" color: {text_color};"
            " font-weight: bold;"
            " font-size: 11px;"
            "}"
        )
        return badge

    def is_pre_fairy_generation(self):
        """Return True when selected generation is before Fairy type existed."""
        gen_index = self.gen_filter.currentIndex()
        return gen_index > 0 and gen_index < 6

    def normalized_team_for_generation(self):
        """Return team copy with Fairy treated as Normal for pre-Gen-6 analyses."""
        normalized_team = []
        pre_fairy = self.is_pre_fairy_generation()

        for pokemon in self.parent.team:
            pokemon_copy = dict(pokemon)
            if pre_fairy:
                if pokemon_copy.get('Type1') == 'Fairy':
                    pokemon_copy['Type1'] = 'Normal'
                if pokemon_copy.get('Type2') == 'Fairy':
                    pokemon_copy['Type2'] = 'Normal'
            normalized_team.append(pokemon_copy)

        return normalized_team

    def remove_team_member(self, index):
        """Remove one Pokemon from the team by index."""
        if 0 <= index < len(self.parent.team):
            self.parent.team.pop(index)
            self.display_team()

    def analyze_team(self):
        """Analyze team with weakness, resistance, and coverage sections."""
        self.clear_analysis()
        if not self.parent.team:
            label = QLabel("No team members to analyze.")
            self.analysis_layout.addWidget(label)
            return

        effective_team = self.normalized_team_for_generation()
        ignored_types = {"Fairy"} if self.is_pre_fairy_generation() else set()
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

        matchups_card = self.build_matchups_card(
            matchup_rows,
            "#F4F8FC"
        )
        coverage_card = self.build_coverage_card(
            profile["coverage"],
            "#F6FBF4"
        )
        missing_types_card = self.build_missing_types_grid_card(
            missing_types,
            "#FFF9F4"
        )

        panel_layout.addWidget(matchups_card)
        panel_layout.addWidget(coverage_card)
        panel_layout.addWidget(missing_types_card)
        self.analysis_layout.addWidget(panel)

    def build_analysis_base_card(self, title, bg_color):
        """Create base card for analysis sections."""
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: 1px solid #C7D4E2; border-radius: 10px; }}")
        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setObjectName("subsection-title")
        layout.addWidget(title_label)

        return card, layout

    def build_matchups_card(self, matchup_rows, bg_color):
        """Build combined defensive matchups section."""
        card, layout = self.build_analysis_base_card("Type Matchups", bg_color)

        if not matchup_rows:
            info = QLabel("No notable defensive matchups")
            layout.addWidget(info)
            layout.addStretch()
            return card

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        columns = 6

        for idx, row in enumerate(matchup_rows):
            severity = self.get_weakness_severity(row["danger"])
            if row["danger"] <= 0 and row["safety"] >= 2:
                severity = "low"

            grid.addWidget(
                self.build_type_metric_tile(
                    row["type"],
                    f"x2:{row['weak_2x']} x4:{row['weak_4x']}\nR:{row['resist_05']} RR:{row['resist_025']} I:{row['immune_0']}",
                    severity=severity,
                ),
                idx // columns,
                idx % columns,
            )

        layout.addLayout(grid)
        layout.addStretch()
        return card

    def build_coverage_card(self, coverage_rows, bg_color):
        """Build offensive coverage section."""
        card, layout = self.build_analysis_base_card("Type Coverage", bg_color)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        columns = 6
        for idx, row in enumerate(coverage_rows):
            coverage_text = f"Super-effective members:{row['super_users']}"

            grid.addWidget(
                self.build_type_metric_tile(
                    row["type"],
                    coverage_text,
                    severity=self.get_coverage_severity(row["super_users"], row["max_attack"])
                ),
                idx // columns,
                idx % columns,
            )

        layout.addLayout(grid)

        layout.addStretch()
        return card

    def build_missing_types_grid_card(self, missing_types, bg_color):
        """Build missing type section using compact badge tiles."""
        card, layout = self.build_analysis_base_card("Missing Types", bg_color)

        if not missing_types:
            info = QLabel("No missing types")
            layout.addWidget(info)
            layout.addStretch()
            return card

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        columns = 6

        for idx, type_name in enumerate(missing_types):
            tile = QFrame()
            tile.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #D9E1EA; border-radius: 8px; }")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(4, 4, 4, 4)
            tile_layout.addWidget(self.create_type_badge(type_name), alignment=Qt.AlignCenter)
            grid.addWidget(tile, idx // columns, idx % columns)

        layout.addLayout(grid)
        layout.addStretch()
        return card

    def build_type_metric_tile(self, type_name, metric_text, severity="neutral"):
        """Build tile containing a type badge and metric details below it."""
        tile = QFrame()
        tile.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #D9E1EA; border-radius: 10px; }")
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(4, 4, 4, 4)
        tile_layout.setSpacing(3)

        type_badge = self.create_type_badge(type_name)
        metric_label = QLabel(metric_text)
        metric_label.setAlignment(Qt.AlignCenter)
        metric_label.setWordWrap(True)
        metric_colors = self.get_metric_severity_colors(severity)
        metric_label.setStyleSheet(
            "QLabel {"
            f" background-color: {metric_colors['bg']};"
            f" border: 1px solid {metric_colors['border']};"
            " border-radius: 10px;"
            " padding: 2px 4px;"
            " font-size: 10px;"
            f" color: {metric_colors['text']};"
            "}"
        )

        type_holder = QWidget()
        type_holder_layout = QHBoxLayout(type_holder)
        type_holder_layout.setContentsMargins(0, 0, 0, 0)
        type_holder_layout.addStretch()
        type_holder_layout.addWidget(type_badge)
        type_holder_layout.addStretch()

        tile_layout.addWidget(type_holder)
        tile_layout.addWidget(metric_label)
        return tile

    def get_metric_severity_colors(self, severity):
        """Map a severity level to badge colors."""
        severity_map = {
            "high": {"bg": "#FDECEC", "border": "#E9A7A7", "text": "#8D1D1D"},
            "medium": {"bg": "#FFF6E5", "border": "#E5C58D", "text": "#7A5410"},
            "low": {"bg": "#EAF8ED", "border": "#9ED6A9", "text": "#1F6A2C"},
            "neutral": {"bg": "#FFFFFF", "border": "#D0D7E2", "text": "#334155"},
        }
        return severity_map.get(severity, severity_map["neutral"])

    def get_weakness_severity(self, danger):
        """Severity for defensive danger score."""
        if danger >= 3:
            return "high"
        if danger >= 1:
            return "medium"
        return "low"

    def get_resistance_severity(self, safety):
        """Severity for resistance strength score."""
        if safety >= 5:
            return "high"
        if safety >= 2:
            return "medium"
        return "low"

    def get_coverage_severity(self, super_users, max_attack):
        """Severity for offensive coverage quality."""
        if super_users >= 3 or max_attack >= 4.0:
            return "low"
        if super_users >= 1 or max_attack > 1.0:
            return "medium"
        return "high"

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

    def clear_analysis(self):
        """Clear analysis results."""
        while self.analysis_layout.count():
            item = self.analysis_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def generate_suggestions(self):
        """Generate team improvement suggestions."""
        self.parent.apply_filters()
        if not self.parent.team:
            self.display_suggestions([])
            return

        effective_team = self.normalized_team_for_generation()
        _, defense_summary, _ = analyze_defense(effective_team)
        ignored_types = {"Fairy"} if self.is_pre_fairy_generation() else None

        suggestions = generate_team_suggestions(
            effective_team,
            self.parent.filtered_data,
            defense_summary,
            ignored_types=ignored_types
        )
        self.display_suggestions(suggestions)

    def display_suggestions(self, suggestions):
        """Display the generated suggestions."""
        # Clear previous suggestions
        while self.suggestions_layout.count():
            item = self.suggestions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        fixed_image_size = 78
        for i, suggestion in enumerate(suggestions):
            name = suggestion['name']
            form = suggestion['form']
            score = round(suggestion['score'], 2)
            role = suggestion['role']

            pokemon = self.parent.pokemon_data[
                (self.parent.pokemon_data['Name'] == name) & (self.parent.pokemon_data['Form'] == form)
            ].iloc[0]
            bst_total = pokemon['Total']
            form_text = f" ({form})" if form != " " else ""
            image_path = get_image_path(pokemon['ID'], name, form)

            suggestion_label = QLabel(
                f"Name: {name}{form_text}\nBST: {bst_total}\nRole: {role}\nScore: {score}"
            )
            suggestion_label.setStyleSheet("QLabel { font-size: 12px; }")

            image_label = QLabel()
            image_label.setFixedSize(fixed_image_size, fixed_image_size)
            image_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    fixed_image_size,
                    fixed_image_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image not found")

            vbox = QVBoxLayout()
            vbox.setContentsMargins(6, 6, 6, 6)
            vbox.setSpacing(6)
            vbox.addWidget(image_label)
            vbox.addWidget(suggestion_label)
            vbox.addWidget(self.build_type_badges_widget(pokemon['Type1'], pokemon['Type2']))
            add_button = QPushButton("Add to Team")
            add_button.setStyleSheet("QPushButton { padding: 6px; font-size: 12px; }")
            add_button.clicked.connect(
                lambda _, n=name, f=form: self.add_suggestion_to_team(n, f)
            )
            vbox.addWidget(add_button)
            widget = QWidget()
            widget.setLayout(vbox)
            widget.setMinimumWidth(148)
            widget.setMaximumWidth(148)
            self.suggestions_layout.addWidget(widget, i // 8, i % 8)

    def add_suggestion_to_team(self, name, form):
        """Add a suggested Pokemon directly to the team."""
        if len(self.parent.team) >= 6:
            return

        duplicate = any(
            member['Name'] == name and member['Form'] == form
            for member in self.parent.team
        )
        if duplicate:
            return

        match = self.parent.filtered_data[
            (self.parent.filtered_data['Name'] == name) &
            (self.parent.filtered_data['Form'].fillna(' ') == form)
        ]
        if len(match) == 0:
            return

        self.parent.team.append(match.iloc[0].to_dict())
        self.display_team()

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