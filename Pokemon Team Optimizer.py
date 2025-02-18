import pandas as pd
import os
import random
import sys
import glob
import re

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QPushButton, QLabel, QListWidget, 
    QListWidgetItem, QComboBox, QMessageBox, QScrollArea, 
    QSizePolicy, QDialog, QCheckBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGridLayout, QSpacerItem, QSizePolicy, QFrame, QSlider, QSpinBox,
    QColorDialog, QStyle, QStyleOptionSlider, QStylePainter, QStyleOptionButton,
    QStyleOptionFrame, QStyleOptionComboBox, QStyleOptionTabWidgetFrame, QTabWidget, QStackedWidget

)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QColor, QBrush, QPen, QPainter, QPolygon, QPolygonF, QRegion
from itertools import combinations


# Load Pokémon data
pokemon_df = pd.read_csv("./data/Pokemon.csv")

# Convert each Pokémon to a dictionary
pokemon_data = []
for _, row in pokemon_df.iterrows():
    pokemon_dict = {
        "ID": row["ID"],
        "Name": row["Name"],
        "Form": row["Form"],
        "Type1": row["Type1"],
        "Type2": row["Type2"],
        "HP": row["HP"],
        "Attack": row["Attack"],
        "Defense": row["Defense"],
        "Sp. Atk": row["Sp. Atk"],
        "Sp. Def": row["Sp. Def"],
        "Speed": row["Speed"],
        "Total": row["Total"],
        "Generation": row["Generation"]
    }
    pokemon_data.append(pokemon_dict)

type_colors = {
    "Normal": "#A8A77A",
    "Fire": "#EE8130",
    "Water": "#6390F0",
    "Electric": "#F7D02C",
    "Grass": "#7AC74C",
    "Ice": "#96D9D6",
    "Fighting": "#C22E28",
    "Poison": "#A33EA1",
    "Ground": "#E2BF65",
    "Flying": "#A98FF3",
    "Psychic": "#F95587",
    "Bug": "#A6B91A",
    "Rock": "#B6A136",
    "Ghost": "#735797",
    "Dragon": "#6F35FC",
    "Dark": "#705746",
    "Steel": "#B7B7CE",
    "Fairy": "#D685AD",
}

form_filter = [
    "Mega", 
    "Primal", 
    "Origin", 
    "Ultra", 
    "Dawn", 
    "Dusk", 
    "Crowned", 
    "Hero", 
    "Eternamax", 
    "Stellar"]

Legendary_ID_filter = [
    144,
    145,
    146,
    150,
    151,
    243,
    244,
    245,
    249,
    250,
    251,
    377,
    378,
    379,
    380,
    381,    
    382,
    383,
    384,
    386,
    480,
    481,
    482,
    483,
    484,
    485,
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493,
    494,
    638,
    639,
    640,
    641,
    642,
    643,
    644,
    645,
    646,
    647,
    648,
    649,
    716,
    717,
    718,
    772,
    773,
    785,
    786,
    787,
    788,
    789,
    790,
    791,
    792,
    800,
    888,
    889,
    890,
    891,
    892,
    894,
    895,
    896,
    897,
    898,
    905,
    1001,
    1002,
    1003,
    1004,
    1007,
    1008,
    1014,
    1015,
    1016,
    1017,
    1024,
]

stylesheet = """
    QMainWindow {
        background-color:rgb(255, 249, 249);
    }
    QLabel {
        color: #333333;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 14px;
    }
    QLabel#title {
        font-size: 24px;
        font-weight: bold;
        color: #2E8B57;
    }
    QLabel#section-title {
        font-size: 20px;
        font-weight: bold;
        color: #2E8B57;
    }
    QLabel#subsection-title {
        font-size: 16px;
        font-weight: bold;
        color: #2E8B57;
    }
    QLineEdit {
        border: 1px solid #2E8B57;
        padding: 5px;
        font-size: 14px;
    }
    QPushButton {
        background-color: #4682B4;
        color: #FFFFFF;
        border: none;
        padding: 10px;
        font-size: 14px;
        font-family: Arial, Helvetica, sans-serif;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5A9BD5;
    }
    QComboBox {
        border: 1px solid #2E8B57;
        padding: 5px;
        font-size: 14px;
    }
    QListWidget {
        border: 1px solid #2E8B57;
        font-size: 14px;
    }
    QScrollArea {
        border: none;
    }
    QTableWidget {
        border: 1px solid #2E8B57;
        font-size: 14px;
    }
    QTableWidget QHeaderView::section {
        background-color:rgb(96, 171, 128);
        color: #FFFFFF;
        padding: 5px;
        border: none;
    }
"""

class PokemonTeamOptimizer(QMainWindow):
######### class PokemonTeamOptimizer(QWidget): #########
    def __init__(self, pokemon_data):
        super().__init__()
        self.pokemon_data = pokemon_data
        self.team = []
        self.pc_box = {}
        self.pc_box_list = []
        self.adding_pokemon = False  # Initialize the flag to prevent multiple additions
        # self.filtered_data = self.pokemon_data.copy()
        self.init_ui()

    def init_ui(self):
        # Apply the stylesheet
        self.setStyleSheet(stylesheet)
        
        # Main Window Settings
        self.setWindowTitle("Pokemon Team Optimizer")
        self.setGeometry(100, 100, 1920, 1200)
        self.showMaximized()
        
        # Create a QTabWidget for tabs
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # --- Tab 1: Team Builder/Viewer and Suggestions ---
        self.team_builder_tab = QWidget()
        self.init_team_builder_tab()
        self.tab_widget.addTab(self.team_builder_tab, "Team Builder")

        # --- Tab 2: PC Widget ---
        self.pc_widget_tab = QWidget()
        self.init_pc_widget_tab()
        self.tab_widget.addTab(self.pc_widget_tab, "PC Widget")

    def init_team_builder_tab(self):
        # Scroll Area for the Team Builder Tab
        scroll_area = QScrollArea(self.team_builder_tab)
        scroll_area.setWidgetResizable(True)

        # Main container for the scrollable content
        content_widget = QWidget()
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setSpacing(20)

        # Title Section
        title_layout = QHBoxLayout()
        title_label = QLabel("Pokemon Team Optimizer")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(title_layout)

        # Search and Filter Section
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(40)

        # Search Section
        search_layout = QVBoxLayout()
        search_label = QLabel("Search Pokémon:")
        search_label.setFixedHeight(20)
        search_layout.addWidget(search_label)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Type to search...")
        self.search_entry.textChanged.connect(self.update_autofill)
        search_layout.addWidget(self.search_entry)

        self.autofill_box = QListWidget()
        self.autofill_box.setFixedHeight(150)
        self.autofill_box.itemClicked.connect(self.add_autofill_to_team)
        search_layout.addWidget(self.autofill_box)

        autofill_button = QPushButton("Add to Team")
        autofill_button.clicked.connect(self.add_autofill_to_team)
        search_layout.addWidget(autofill_button)

        search_container = QWidget()
        search_container.setLayout(search_layout)
        search_container.setFixedWidth(250)
        search_filter_layout.addWidget(search_container, alignment=Qt.AlignCenter)

        # Filters Section
        filters_layout = QVBoxLayout()
        filters_label = QLabel("Filters")
        filters_layout.addWidget(filters_label)

        # Gen Filter
        gen_filter_label = QLabel("Generation:")
        filters_layout.addWidget(gen_filter_label)
        self.gen_filter = QComboBox()
        self.gen_filter.addItems(["All Generations", "Gen 1", "Gen 2", "Gen 3", "Gen 4", "Gen 5", "Gen 6", "Gen 7", "Gen 8", "Gen 9"])
        self.gen_filter.currentIndexChanged.connect(self.update_autofill)
        filters_layout.addWidget(self.gen_filter)

        # Mega and Legendary Filters
        mega_filter_label = QLabel("Mega & Special Forms [Y/N]:")
        filters_layout.addWidget(mega_filter_label)
        self.mega_filter = QCheckBox("Include Mega and Special Forms")
        self.mega_filter.setChecked(False)
        self.mega_filter.stateChanged.connect(self.update_autofill)
        filters_layout.addWidget(self.mega_filter)

        # On/Off for legendaries
        legendary_filter_label = QLabel("Legendaries [Y/N]:")
        filters_layout.addWidget(legendary_filter_label)
        self.legendary_filter = QCheckBox("Include Legendaries")
        self.legendary_filter.setChecked(True)
        self.legendary_filter.stateChanged.connect(self.update_autofill)
        filters_layout.addWidget(self.legendary_filter)

        type_filter_label = QLabel("Type (only for Analysis):")
        filters_layout.addWidget(type_filter_label)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"])
        self.type_filter.currentIndexChanged.connect(self.update_autofill)
        filters_layout.addWidget(self.type_filter)

        filters_container = QWidget()
        filters_container.setLayout(filters_layout)
        filters_container.setFixedWidth(250)
        search_filter_layout.addWidget(filters_container, alignment=Qt.AlignLeft)

        self.main_layout.addLayout(search_filter_layout)
        self.main_layout.setAlignment(search_filter_layout, Qt.AlignCenter)

        # Team Display Section
        team_label = QLabel("My Team:")
        team_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.main_layout.addWidget(team_label, alignment=Qt.AlignCenter)

        self.team_layout = QHBoxLayout()
        team_container = QWidget()
        team_container.setLayout(self.team_layout)

        clear_button = QPushButton("Clear Team")
        clear_button.clicked.connect(self.clear_team)
        self.main_layout.addWidget(clear_button, alignment=Qt.AlignCenter)

        self.main_layout.addWidget(team_container)

        # Analysis Section
        analysis_label = QLabel("Team Analysis:")
        analysis_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.main_layout.addWidget(analysis_label, alignment=Qt.AlignCenter)

        # Analysis Buttons
        analysis_buttons_layout = QHBoxLayout()
        analysis_buttons_layout.setAlignment(Qt.AlignCenter)

        analysis_button = QPushButton("Analyze Team")
        analysis_button.clicked.connect(self.show_team_analysis)
        analysis_buttons_layout.addWidget(analysis_button)

        clear_analysis_button = QPushButton("Clear Analysis")
        clear_analysis_button.clicked.connect(self.clear_analysis)
        analysis_buttons_layout.addWidget(clear_analysis_button)

        self.main_layout.addLayout(analysis_buttons_layout)

        # Defense Analysis Label
        defense_analysis_label = QLabel("Defense Analysis:")
        defense_analysis_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(defense_analysis_label, alignment=Qt.AlignCenter)

        self.def_analysis_widget = QWidget()
        self.def_analysis_widget.setLayout(QVBoxLayout())
        self.main_layout.addWidget(self.def_analysis_widget)

        # Attack Analysis Label
        attack_analysis_label = QLabel("Attack Analysis:")
        attack_analysis_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(attack_analysis_label, alignment=Qt.AlignCenter)

        self.atk_analysis_widget = QWidget()
        self.atk_analysis_widget.setLayout(QVBoxLayout())
        self.main_layout.addWidget(self.atk_analysis_widget)

        # Missing Types Widget
        self.missing_types_label = QLabel("Missing Types:")
        self.missing_types_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.missing_types_label, alignment=Qt.AlignCenter)
        
        self.missing_types_widget = QWidget()
        self.missing_types_widget.setLayout(QVBoxLayout())
        self.main_layout.addWidget(self.missing_types_widget, alignment=Qt.AlignCenter)

        # Team Suggestions Section
        suggestions_label = QLabel("Team Suggestions:")
        attack_analysis_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(suggestions_label, alignment=Qt.AlignCenter)

        # Button Suggestions Widget
        suggestion_button_layout = QHBoxLayout()
        suggestion_button_layout.setAlignment(Qt.AlignCenter)

        suggestions_button = QPushButton("Generate Suggestions")
        suggestions_button.clicked.connect(self.generate_suggestions)
        suggestion_button_layout.addWidget(suggestions_button)

        clear_suggestions_button = QPushButton("Clear Suggestions")
        clear_suggestions_button.clicked.connect(self.clear_suggestions)
        suggestion_button_layout.addWidget(clear_suggestions_button)

        self.main_layout.addLayout(suggestion_button_layout)

        # Suggestions Widget
        self.suggestions_widget = QWidget()
        self.suggestions_layout = QGridLayout()  # Store the layout in an instance variable
        self.suggestions_widget.setLayout(self.suggestions_layout)
        self.main_layout.addWidget(self.suggestions_widget, alignment=Qt.AlignCenter)

        scroll_area.setWidget(content_widget)
        main_layout = QVBoxLayout(self.team_builder_tab)
        main_layout.addWidget(scroll_area)

    def init_pc_widget_tab(self):
        
        # Scroll Area for the Team Builder Tab
        PC_Box_scroll_area = QScrollArea(self.pc_widget_tab)
        PC_Box_scroll_area.setWidgetResizable(True)

        # Main container for the scrollable content
        PC_Box_content_widget = QWidget()
        self.PC_Box_main_layout = QVBoxLayout(PC_Box_content_widget)
        self.PC_Box_main_layout.setSpacing(20)

        # Title Section
        PC_Box_title_layout = QHBoxLayout()
        PC_Box_title_label = QLabel("Pokemon Team Optimizer")
        PC_Box_title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        PC_Box_title_layout.addWidget(PC_Box_title_label, alignment=Qt.AlignCenter)
        self.PC_Box_main_layout.addLayout(PC_Box_title_layout)
        
        # PC Box Search Section
        
        PC_Box_search_layout = QVBoxLayout()
        PC_Box_search_label = QLabel("Add Pokémon to PC-Box:")
        PC_Box_search_label.setFixedHeight(20)
        PC_Box_search_layout.addWidget(PC_Box_search_label, alignment=Qt.AlignCenter)

        # Search and Filter Section
        PC_Box_search_filter_layout = QHBoxLayout()
        PC_Box_search_filter_layout.setSpacing(40)

        self.PC_Box_search_entry = QLineEdit()
        self.PC_Box_search_entry.setPlaceholderText("Type to search...")
        self.PC_Box_search_entry.textChanged.connect(self.PC_Box_update_autofill)
        PC_Box_search_layout.addWidget(self.PC_Box_search_entry, alignment=Qt.AlignCenter)

        self.PC_Box_autofill_box = QListWidget()
        self.PC_Box_autofill_box.setFixedHeight(150)
        self.PC_Box_autofill_box.itemClicked.connect(self.PC_Box_add_autofill)
        PC_Box_search_layout.addWidget(self.PC_Box_autofill_box, alignment=Qt.AlignCenter)

        PC_Box_autofill_button = QPushButton("Add to PC Box")
        PC_Box_autofill_button.clicked.connect(self.PC_Box_add_autofill)
        PC_Box_search_layout.addWidget(PC_Box_autofill_button, alignment=Qt.AlignCenter)

        # Search Container
        PC_Box_search_container = QWidget()
        PC_Box_search_container.setLayout(PC_Box_search_layout)
        PC_Box_search_container.setFixedWidth(250)
        PC_Box_search_filter_layout.addWidget(PC_Box_search_container, alignment=Qt.AlignCenter)

        # Gen Filter
        PC_Box_filters_layout = QVBoxLayout()
        PC_Box_gen_filter_label = QLabel("Generation:")
        PC_Box_filters_layout.addWidget(PC_Box_gen_filter_label)
        self.PC_Box_gen_filter = QComboBox()
        self.PC_Box_gen_filter.addItems(["All Generations", "Gen 1", "Gen 2", "Gen 3", "Gen 4", "Gen 5", "Gen 6", "Gen 7", "Gen 8", "Gen 9"])
        self.PC_Box_gen_filter.currentIndexChanged.connect(self.PC_Box_update_autofill)
        PC_Box_filters_layout.addWidget(self.PC_Box_gen_filter)

        PC_Box_filters_container = QWidget()
        PC_Box_filters_container.setLayout(PC_Box_filters_layout)
        PC_Box_filters_container.setFixedWidth(250)
        PC_Box_search_filter_layout.addWidget(PC_Box_filters_container, alignment=Qt.AlignLeft)

        self.PC_Box_main_layout.addLayout(PC_Box_search_filter_layout)
        self.PC_Box_main_layout.setAlignment(PC_Box_search_filter_layout, Qt.AlignCenter)

        # PC Box Display Section
        PC_Box_team_label = QLabel("My PC Box:")
        PC_Box_team_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.PC_Box_main_layout.addWidget(PC_Box_team_label, alignment=Qt.AlignCenter)
        
        self.PC_Box_Widget = QWidget()
        self.PC_Box_layout = QGridLayout()  # Initialize the layout for displaying Pokémon
        self.PC_Box_Widget.setLayout(self.PC_Box_layout)
        self.PC_Box_Widget.setFixedSize(1422, 800)

        # Add the background image as a separate label
        self.background_label = QLabel(self.PC_Box_Widget)
        pixmap = QPixmap("./data/misc_images/Box_Fist.png")
        scaled_pixmap = pixmap.scaled(self.PC_Box_Widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, 1422, 800)
        self.background_label.lower()  # Ensure it stays in the background

        self.PC_Box_main_layout.addWidget(self.PC_Box_Widget, alignment=Qt.AlignCenter)

        # clear PC Box Button
        PC_Box_clear_button = QPushButton("Clear PC Box")
        PC_Box_clear_button.clicked.connect(self.PC_Box_clear_team)
        self.PC_Box_main_layout.addWidget(PC_Box_clear_button, alignment=Qt.AlignCenter)

        # Add "Build Team" button
        self.build_team_button = QPushButton("Build Team")
        self.build_team_button.clicked.connect(self.PC_Box_build_team)
        self.PC_Box_main_layout.addWidget(self.build_team_button, alignment=Qt.AlignCenter)

        # PC Box Suggestions Section + Widget
        PC_Box_suggestions_label = QLabel("PC Box Team Suggestions:")
        PC_Box_suggestions_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.PC_Box_main_layout.addWidget(PC_Box_suggestions_label, alignment=Qt.AlignCenter)
        PC_Box_Team_suggestions_widget = QWidget()
        self.PC_Box_Team_suggestions_layout = QGridLayout()  # Store the layout in an instance variable
        PC_Box_Team_suggestions_widget.setLayout(self.PC_Box_Team_suggestions_layout)
        self.PC_Box_main_layout.addWidget(PC_Box_Team_suggestions_widget, alignment=Qt.AlignCenter)

        # Set up the scrollable area
        PC_Box_scroll_area.setWidget(PC_Box_content_widget)
        PC_Box_main_layout = QVBoxLayout(self.pc_widget_tab)
        PC_Box_main_layout.addWidget(PC_Box_scroll_area)

####### Search Section #######
    
    def update_team_view(self):
        # Clear existing team view
        while self.team_layout.count():
            child = self.team_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Display each Pokémon in the team
        self.display_team()

    def update_autofill(self):
        if not hasattr(self, 'filtered_data'):
            self.filtered_data = self.pokemon_data.copy()

        query = self.search_entry.text().strip().lower()

        if query:
            try:
                filtered_data = self.pokemon_data[
                    self.pokemon_data['Name'].str.lower().str.contains(query, na=False) |
                    self.pokemon_data['Form'].str.lower().str.contains(query, na=False)
                ]
            
            except re.error:
                print(f"Error in filtering: {re.error}")
                filtered_data = pd.DataFrame()

        else:
            filtered_data = self.pokemon_data.copy()


       # Filter Pokémon by generation
        gen_index = self.gen_filter.currentIndex()
        if gen_index > 0:
            filtered_data = filtered_data[filtered_data['Generation'] <= gen_index]

        # Adjust Fairy type for generations below 6
        if gen_index < 6:
            filtered_data.loc[filtered_data['Type1'] == 'Fairy', 'Type1'] = 'Normal'
            filtered_data.loc[filtered_data['Type2'] == 'Fairy', 'Type2'] = 'Normal'

        # Filter Pokémon by mega evolution and special forms
        if not self.mega_filter.isChecked():
            filtered_data = filtered_data[~filtered_data['Form'].str.contains('|'.join(form_filter))]

        # Filter Pokémon by legendaries if the column exists
        if not self.legendary_filter.isChecked():
            filtered_data = filtered_data[~filtered_data['ID'].isin(Legendary_ID_filter)]

        # Filter Pokémon by type
        type_filter = self.type_filter.currentText()
        if type_filter != "All Types":
            filtered_data = filtered_data[
                (filtered_data['Type1'] == type_filter) | (filtered_data['Type2'] == type_filter)
            ]

        # Update the autofill box with the filtered Pokémon
        self.filtered_data = filtered_data
        self.autofill_box.clear()
        for _, pokemon in filtered_data.iterrows():
            self.autofill_box.addItem(pokemon['Name'])

        # Add suggestions to the autofill box (based on name and form, without parentheses)
        for _, row in self.filtered_data.iterrows():
            name = row['Name']
            form = row['Form'].strip()

            if form:
                # If form exists, append the form with a hyphen (no parentheses)
                display_name = f"{name}-{form}"
            else:
                display_name = name

            self.autofill_box.addItem(display_name)

        self.populate_autofill_box(self.filtered_data.head(5)) 

    def populate_autofill_box(self, autofill):
        self.autofill_box.clear()  # Clear existing items
        max_items = 5  # Maximum number of items to display
        item_height = 30  # Adjust this value based on your item height
        for index, (_, pokemon) in enumerate(autofill.iterrows()):
            if index >= max_items:
                break
            # Display the form in parentheses if available
            form_suffix = f" ({pokemon['Form'].strip()})" if pokemon['Form'].strip() else ""
            self.autofill_box.addItem(f"{pokemon['Name']}{form_suffix}")
        
        # Set the height of the QListWidget to always display 5 items
        self.autofill_box.setFixedHeight(max_items * item_height)

    def add_autofill_to_team(self):
        print("add_autofill_to_team called")  # Debug print statement
        if self.adding_pokemon:
            print("Already adding a Pokémon, skipping...")  # Debug print statement
            return  # Prevent multiple additions

        self.adding_pokemon = True  # Set the flag to prevent multiple additions
        # Check if the team is already full

        try:
            # Check if the team is already full
            if len(self.team) >= 6:
                QMessageBox.warning(self, "Team Full", "You can only have up to 6 Pokémon in your team!")
                return

            # Get the selected item from the autofill box
            current_item = self.autofill_box.currentItem()
            if not current_item:
                print("No item selected")  # Debug print statement
                return  # No item selected

            # Extract the full name including the form from the list
            selected_name = current_item.text()
            print(f"Selected name: {selected_name}")  # Debug print statement

            # Split the name and form
            name_and_form = selected_name.split(" (")
            name = name_and_form[0].strip()
            form = name_and_form[1].rstrip(")") if len(name_and_form) > 1 else ""

            # Find the Pokémon data matching the name and form
            selected_pokemon = self.pokemon_data[
                (self.pokemon_data['Name'] == name) &
                (self.pokemon_data['Form'].str.strip() == form)
            ]

            if not selected_pokemon.empty:
                # Add Pokémon to the team
                pokemon_dict = selected_pokemon.iloc[0].to_dict()
                self.add_to_team(pokemon_dict)

                # Remove the added Pokémon from the autofill box
                self.autofill_box.takeItem(self.autofill_box.currentRow())  # Removes it from the list

                # Update the team view to reflect the added Pokémon
                self.update_team_view()

                # Optionally, refresh the autofill list to ensure it's up-to-date
                self.update_autofill()
        finally:
            self.adding_pokemon = False  # Reset the flag

        # Clear the selection to prevent multiple additions
        self.autofill_box.clearSelection()

    def add_to_team(self, pokemon):
        self.team.append(pokemon)
        self.team = self.team[:6]  # Limit the team size to 6
        self.display_team()

######## Team Viewer Section ########

    def setup_team_view(self):
        self.team_view = QScrollArea(self)

    def display_team(self):
        def get_random_image_path(pokemon_id, name, form):
            base_folder = r"./data/pokemon_images"
            
            form_suffix = f"-{form}" if form != " " else ""

            pattern = f"{base_folder}/{pokemon_id}_*_{name}{form_suffix}.png"
            matching_files = glob.glob(pattern)
            # print(pattern)
            if matching_files:
                return random.choice(matching_files)
            # If no images are found, return a placeholder image
            return "./data/misc_images/substitute.png"

        # Clear the current team layout
        for i in reversed(range(self.team_layout.count())):
            widget = self.team_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # Remove the widget (Pokémon image or card)

        parent_widget = self.team_layout.parentWidget()
        if parent_widget:
            parent_widget.update()
            parent_widget.repaint()

        # check if fairy type must be changed to normal for generations below 6
        if self.gen_filter.currentIndex() < 6 and self.gen_filter.currentIndex() > 0:
            for pokemon in self.team:
                if pokemon['Type1'] == 'Fairy':
                    pokemon['Type1'] = 'Normal'
                if pokemon['Type2'] == 'Fairy':
                    pokemon['Type2'] = ' '

        # Display each Pokémon in the team
        for index, pokemon in enumerate(self.team):
            # Get the Pokémon's image
            pokemon_id = pokemon["ID"]
            name = pokemon["Name"]
            form = pokemon["Form"]

            img_path = get_random_image_path(pokemon_id, name, form)

            # Create a widget for this Pokémon
            pokemon_widget = QWidget()
            layout = QVBoxLayout()

            img_label = QLabel()
            if os.path.exists(img_path):
                # print(f"Image path exists: {img_path}")
                pixmap = QPixmap(img_path)
                if pixmap.isNull():
                    print(f"Failed to load image: {img_path}")  # Debug print statement
                    pixmap = QPixmap("./data/misc_images/substitute.png")
                    if pixmap.isNull():
                        print("Failed to load substitute image")  # Debug print statement
                    else:
                        pixmap = QPixmap(img_path).scaled(100, 100, Qt.KeepAspectRatio)
                        # print(f"Scaled pixmap size: {pixmap.size()}")
                        # print(f"Scaled pixmap size: {pixmap.width()}x{pixmap.height()}")
                        img_label.setPixmap(pixmap)

                    # print("Substitute image loaded")  # Debug print statement
                else:
                    img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                    if pixmap.isNull():
                        # print(f"Failed to load image: {img_path}")  # Debug print statement
                        pixmap = QPixmap("./data/misc_images/substitute.png")
                        if pixmap.isNull():
                            print("Failed to load substitute image")  # Debug print statement
                        else:
                            pixmap = QPixmap(img_path).scaled(100, 100, Qt.KeepAspectRatio)
                            # print(f"Scaled pixmap size: {pixmap.size()}")
                            # print(f"Scaled pixmap size: {pixmap.width()}x{pixmap.height()}")
                            img_label.setPixmap(pixmap)
                    
            else:
                print(f"Image path does not exist: {img_path}")
                pixmap = QPixmap("./data/misc_images/substitute.png")
                if pixmap.isNull():
                    print("Failed to load substitute image")  # Debug print statement
                else:
                    img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

            #img_label = QLabel("Image Placeholder")

            img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label) 

            # Pokémon Name, potential Forms and Types
            if pokemon["Form"] != " ":
                if pokemon['Type2'] != " ":
                    name_label = QLabel(f"{pokemon['Name']} ({pokemon['Form']})")
                else:
                    name_label = QLabel(f"{pokemon['Name']} ({pokemon['Form']})")
            else:
                if pokemon['Type2'] != " ":
                    name_label = QLabel(f"{pokemon['Name']}")
                else:
                    name_label = QLabel(f"{pokemon['Name']}")

            # Pokémon Name
            # name_label = QLabel(pokemon['Name'])
            name_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_label)

            # print(f"Pokemon: {pokemon['Name']}, Type1: {pokemon['Type1']}, Type2: {pokemon['Type2']}")  # Debug print statement

            # Pokémon Types with colored text
            type1_color = type_colors.get(pokemon['Type1'], "#000000")  # Default to black if type not found
            type1_label = QLabel(pokemon['Type1'])
            type1_label.setStyleSheet(f"color: {type1_color}; font-weight: bold;")
            type1_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(type1_label)

            if pokemon['Type2'] and pokemon['Type2'] != " ":
                type2_color = type_colors.get(pokemon['Type2'], "#000000")  # Default to black if type not found
                type2_label = QLabel(pokemon['Type2'])
                type2_label.setStyleSheet(f"color: {type2_color}; font-weight: bold;")
                type2_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(type2_label)

            # Pokémon Total base stats with button to see the detailed stats
            total_label = QLabel(f"BST: {pokemon['Total']}")
            total_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(total_label)

            # Add a button to toggle the visibility of detailed stats
            toggle_button = QPushButton("Show Detailed Stats")
            toggle_button.setFixedWidth(150)
            layout.addWidget(toggle_button, alignment=Qt.AlignCenter)

            # Add detailed stats directly to the layout, initially hidden
            stats_widget = QWidget()
            stats_layout = QVBoxLayout()
            stats_widget.setLayout(stats_layout)
            stats_widget.setVisible(False)  # Initially hidden

            stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
            for stat in stats:
                if stat in pokemon:
                    stat_label = QLabel(f"{stat}: {pokemon[stat]}")
                    stat_label.setObjectName(f"{stat}_label")  # Set object name for easy reference
                    stat_label.setAlignment(Qt.AlignCenter)
                    stats_layout.addWidget(stat_label)
                else:
                    print(f"Key '{stat}' not found in pokemon dictionary")  # Debug print statement

            stats_widget.setObjectName("stats_widget")  # Set object name for easy reference
            layout.addWidget(stats_widget)

            # Connect the toggle button to show/hide the detailed stats
            toggle_button.clicked.connect(lambda _, sw=stats_widget, tb=toggle_button: self.toggle_stats(sw, tb))

            # Remove Button
            remove_button = QPushButton("Remove")
            remove_button.setFixedWidth(150)
            remove_button.clicked.connect(self.get_remove_pokemon_function(index))
            layout.addWidget(remove_button, alignment=Qt.AlignCenter)

            # Add the layout to the main team layout
            pokemon_widget.setLayout(layout)
            self.team_layout.addWidget(pokemon_widget)

        # Update and repaint the parent widget to ensure the layout is updated
        if parent_widget:
            parent_widget.update()
            parent_widget.repaint()

    def toggle_stats(self, stats_widget, toggle_button):
        if stats_widget.isVisible():
            stats_widget.setVisible(False)
            toggle_button.setText("Show Detailed Stats")
        else:
            stats_widget.setVisible(True)
            toggle_button.setText("Hide Detailed Stats")
     
    def get_remove_pokemon_function(self, index):

        def remove_pokemon():
            self.remove_pokemon_from_team(index)

        return remove_pokemon
                                                     
    def remove_pokemon_from_team(self, index):
        if 0 <= index < len(self.team):
            del self.team[index]
            self.display_team()

    def clear_team(self):
        for i in reversed(range(self.team_layout.count())):
            widget = self.team_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # Remove the widget (Pokémon image or card)
        
        # Clear the team list
        self.team = []

####### Analysis Section #######
    def show_team_analysis(self):
        # Get important values for the analysis
        individual_defense, summary_matrix, attack_types, effectiveness_levels = self.analyze_defense()
        self.fun_def_analysis_widget(individual_defense, summary_matrix, attack_types, effectiveness_levels)
        self.highlight_highest_stats()
        individual_attack, summary_matrix, defend_types, effectiveness_levels = self.analyze_attack()
        self.fun_atk_analysis_widget(individual_attack, summary_matrix, defend_types, effectiveness_levels)
        self.analyze_missing_types()

    def highlight_highest_stats(self):
        # Find the two highest values for each stat
        stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
        highest_stats = {stat: [] for stat in stats}
        for stat in stats:
            values = [pokemon[stat] for pokemon in self.team if stat in pokemon]
            if values:
                highest_stats[stat] = sorted(values, reverse=True)[:2]

        # print(f"Highest stats: {highest_stats}")  # Debug print statement

         # Highlight the two highest values for each stat
        for i in range(self.team_layout.count()):
            widget = self.team_layout.itemAt(i).widget()
            if widget:
                stats_widget = widget.findChild(QWidget, "stats_widget")
                if stats_widget:
                    for stat in stats:
                        for child in stats_widget.children():
                            if isinstance(child, QLabel) and child.objectName() == f"{stat}_label":
                                if int(child.text().split(": ")[1]) in highest_stats[stat]:
                                    child.setStyleSheet("color: red; font-weight: bold;")
                                    # print(f"Pokemon with highest {stat}: {child.text()}")

    def fun_def_analysis_widget(self, individual_defense, summary_matrix, attack_types, effectiveness_levels):
        layout = self.def_analysis_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

         # Create and add the tables
        defense_table = self.create_individual_defense_table(individual_defense, attack_types)
        summary_table = self.create_summary_def_table(summary_matrix, attack_types, effectiveness_levels)

        # Set size policies to expand vertically
        defense_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        summary_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

       # Calculate the required height for the tables
        table_height = defense_table.verticalHeader().length() + defense_table.horizontalHeader().height() + 214
        # print(f"Table height: {table_height}")
        defense_table.setFixedHeight(table_height)
        summary_table.setFixedHeight(table_height)

        # Create a horizontal layout to place the tables side by side
        tables_layout = QHBoxLayout()
        tables_layout.addWidget(defense_table)
        tables_layout.addWidget(summary_table)

        # Add the tables layout to the analysis widget layout
        layout.addLayout(tables_layout)

        # Ensure the analysis widget expands to fit the tables
        self.def_analysis_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.def_analysis_widget.setFixedHeight(table_height)

    def fun_atk_analysis_widget(self, individual_attack, summary_matrix, defend_types, effectiveness_levels):
        layout = self.atk_analysis_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create and add the tables
        attack_table = self.create_individual_attack_table(individual_attack, defend_types)
        summary_table = self.create_summary_attack_table(summary_matrix, defend_types, effectiveness_levels)

        # Set size policies to expand vertically
        attack_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        summary_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Calculate the required height for the tables
        table_height = attack_table.verticalHeader().length() + attack_table.horizontalHeader().height() + 214
        # print(f"Table height: {table_height}")
        attack_table.setFixedHeight(table_height)
        summary_table.setFixedHeight(table_height)

        # Create a horizontal layout to place the tables side by side
        tables_layout = QHBoxLayout()
        tables_layout.addWidget(attack_table)
        tables_layout.addWidget(summary_table)

        # Add the tables layout to the analysis widget layout
        layout.addLayout(tables_layout)

        # Ensure the analysis widget expands to fit the tables
        self.atk_analysis_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.atk_analysis_widget.setFixedHeight(table_height)

    def analyze_defense(self):
        if not hasattr(self, 'def_analysis_widget'):
            self.def_analysis_widget = QWidget()
            self.def_analysis_widget.setLayout(QVBoxLayout())
            self.main_layout.addWidget(self.def_analysis_widget)

        type_chart_defense = {
            "Normal": {"Fighting": 2, "Ghost": 0},
            "Fire": {
                "Fire": 0.5,
                "Water": 2,
                "Grass": 0.5,
                "Ice": 0.5,
                "Ground": 2,
                "Bug": 0.5,
                "Rock": 2,
                "Steel": 0.5,
                "Fairy": 0.5,
            },
            "Water": {
                "Fire": 0.5,
                "Water": 0.5,
                "Electric": 2,
                "Grass": 2,
                "Ice": 0.5,
                "Steel": 0.5
            },
            "Electric": {
                "Electric": 0.5,
                "Ground": 2,
                "Flying": 0.5,
                "Steel": 0.5
            },
            "Grass": {
                "Fire": 2,
                "Water": 0.5,
                "Electric": 0.5,
                "Grass": 0.5,
                "Ice": 2,
                "Poison": 2,
                "Ground": 0.5,
                "Flying": 2,
                "Bug": 2
            },
            "Ice": {
                "Fire": 2,
                "Ice": 0.5,
                "Fighting": 2,
                "Rock": 2,
                "Steel": 2
            },
            "Fighting": {
                "Flying": 2,
                "Psychic": 2,
                "Bug": 0.5,
                "Rock": 0.5,
                "Dark": 0.5,
                "Fairy": 2
            },
            "Poison": {
                "Grass": 0.5,
                "Fighting": 0.5,
                "Poison": 0.5,
                "Ground": 2,
                "Psychic": 2,
                "Bug": 0.5,
                "Fairy": 0.5
            },
            "Ground": {
                "Water": 2,
                "Electric": 0,
                "Grass": 2,
                "Ice": 2,
                "Poison": 0.5,
                "Rock": 0.5
            },
            "Flying": {
                "Electric": 2,
                "Ice": 2,
                "Rock": 2,
                "Grass": 0.5,
                "Fighting": 0.5,
                "Bug": 0.5,
                "Ground": 0
            },
            "Psychic": {
                "Fighting": 0.5,
                "Psychic": 0.5,
                "Bug": 2,
                "Ghost": 2,
                "Dark": 2
            },
            "Bug": {
                "Fire": 2,
                "Grass": 0.5,
                "Fighting": 0.5,
                "Ground": 0.5,
                "Flying": 2,
                "Rock": 2
            },
            "Rock": {
                "Normal": 0.5,
                "Fire": 0.5,
                "Water": 2,
                "Grass": 2,
                "Fighting": 2,
                "Poison": 0.5,
                "Ground": 2,
                "Flying": 0.5,
                "Steel": 2
            },
            "Ghost": {
                "Normal": 0,
                "Fighting": 0,
                "Poison": 0.5,
                "Bug": 0.5,
                "Ghost": 2,
                "Dark": 2
            },
            "Dragon": {
                "Fire": 0.5,
                "Water": 0.5,
                "Grass": 0.5,
                "Electric": 0.5,
                "Ice": 2,
                "Dragon": 2,
                "Fairy": 2
            },
            "Dark": {
                "Fighting": 2,
                "Psychic": 0,
                "Bug": 2,
                "Ghost": 0.5,
                "Dark": 0.5,
                "Fairy": 2
            },
            "Steel": {
                "Normal": 0.5,
                "Fire": 2,
                "Grass": 0.5,
                "Ice": 0.5,
                "Fighting": 2,
                "Poison": 0,
                "Ground": 2,
                "Flying": 0.5,
                "Psychic": 0.5,
                "Bug": 0.5,
                "Rock": 0.5,
                "Dragon": 0.5,
                "Steel": 0.5,
                "Fairy": 0.5
            },
            "Fairy": {
                "Fighting": 0.5,
                "Poison": 2,
                "Bug": 0.5,
                "Dragon": 0,
                "Dark": 0.5,
                "Steel": 2
            }
        }

        # Initialize summary matrix
        attack_types = list(type_chart_defense.keys())
        effectiveness_levels = ["immunities", "x0.25", "x0.5","x1","x2", "x4"]
        
        # Initialize summary matrix
        summary_matrix = {t: {e: 0 for e in effectiveness_levels} for t in attack_types}

        # Individual defense factors for each Pokémon
        individual_defense = {t: [] for t in attack_types}

        for pokemon in self.team:
            # Pokemon with fairy type in generations below 6 must have their type changed to normal
            if self.gen_filter.currentIndex() < 6 and self.gen_filter.currentIndex() > 0 and (pokemon['Type1'] == 'Fairy' or pokemon['Type2']) == 'Fairy':
                if pokemon['Type1'] == 'Fairy':
                    pokemon['Type1'] = 'Normal'
                if pokemon['Type2'] == 'Fairy':
                    pokemon['Type2'] = ' '

            type1 = pokemon['Type1']
            type2 = pokemon['Type2'] if pokemon['Type2'] != " " else None

            for attack_type in attack_types:
                factor1 = type_chart_defense.get(type1, {}).get(attack_type, 1)
                factor2 = type_chart_defense.get(type2, {}).get(attack_type, 1) if type2 else 1
                effectiveness = factor1 * factor2

                # Add to individual defense
                individual_defense[attack_type].append(effectiveness)

                # Update summary matrix
                if effectiveness == 0:
                    summary_matrix[attack_type]["immunities"] += 1
                elif effectiveness == 4:
                    summary_matrix[attack_type]["x4"] += 1
                elif effectiveness == 2:
                    summary_matrix[attack_type]["x2"] += 1
                elif effectiveness == 1:
                    summary_matrix[attack_type]["x1"] += 1
                elif effectiveness == 0.5:
                    summary_matrix[attack_type]["x0.5"] += 1
                elif effectiveness == 0.25:
                    summary_matrix[attack_type]["x0.25"] += 1

        # Debug Print
        # print("Individual Defense:", individual_defense)
        # print("Summary Matrix:", summary_matrix)

        return individual_defense, summary_matrix, attack_types, effectiveness_levels

    def create_individual_defense_table(self, individual_defense, attack_types):
        pokemon_names = [pokemon['Name'] for pokemon in self.team]
        
        table = QTableWidget()
        table.setRowCount(len(attack_types))
        table.setColumnCount(len(pokemon_names))

        # Set headers
        table.setVerticalHeaderLabels(attack_types)
        table.setHorizontalHeaderLabels(pokemon_names)

        # Populate table
        for row, attack_type in enumerate(attack_types):
            for col, effectiveness in enumerate(individual_defense[attack_type]):
                item = QTableWidgetItem(f"{effectiveness:.2f}")
                item.setTextAlignment(Qt.AlignCenter)

                # Color coding
                if effectiveness == 0:
                    item.setBackground(QColor(200, 200, 200))  # Gray for immunity
                elif effectiveness == 4:
                    item.setBackground(QColor(255, 100, 100))  # Intense red
                elif effectiveness == 2:
                    item.setBackground(QColor(255, 150, 150))  # Lighter red
                elif effectiveness == 0.5:
                    item.setBackground(QColor(150, 255, 150))  # Light green
                elif effectiveness == 0.25:
                    item.setBackground(QColor(100, 255, 100))  # Intense green

                table.setItem(row, col, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def create_summary_def_table(self, summary_matrix, attack_types, effectiveness_levels):
        table = QTableWidget()
        table.setRowCount(len(attack_types))
        table.setColumnCount(len(effectiveness_levels))

        # Set headers
        table.setVerticalHeaderLabels(attack_types)
        table.setHorizontalHeaderLabels(effectiveness_levels)

        # Populate table
        for row, attack_type in enumerate(attack_types):
            for col, effectiveness in enumerate(effectiveness_levels):
                value = summary_matrix[attack_type][effectiveness]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                # Color coding
                if effectiveness == "x4" and value > 0:
                    item.setBackground(QColor(255, 100, 100))  # Intense red
                elif effectiveness == "x2" and value > 0:
                    item.setBackground(QColor(255, 150, 150))  # Lighter red
                elif effectiveness == "x0.5" and value > 0:
                    item.setBackground(QColor(150, 255, 150))  # Light green
                elif effectiveness == "x0.25" and value > 0:
                    item.setBackground(QColor(100, 255, 100))  # Intense green
                elif effectiveness == "immunities" and value > 0:
                    item.setBackground(QColor(200, 200, 200))  # Gray
                else:
                    item.setBackground(QColor(255, 255, 255))  # White for x1

                table.setItem(row, col, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def analyze_attack(self):
        if not hasattr(self, 'atk_analysis_widget'):
            self.atk_analysis_widget = QWidget()
            self.atk_analysis_widget.setLayout(QVBoxLayout())
            self.main_layout.addWidget(self.atk_analysis_widget)

        type_chart_attack = {
            "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
            "Fire": {
                "Fire": 0.5,
                "Water": 0.5,
                "Grass": 2,
                "Ice": 2,
                "Bug": 2,
                "Rock": 0.5,
                "Dragon": 0.5,
                "Steel": 2
            },
            "Water": {
                "Fire": 2,
                "Water": 0.5,
                "Grass": 0.5,
                "Ground": 2,
                "Rock": 2,
                "Dragon": 0.5
            },
            "Electric": {
                "Water": 2,
                "Electric": 0.5,
                "Grass": 0.5,
                "Ground": 0,
                "Flying": 2,
                "Dragon": 0.5
            },
            "Grass": {
                "Fire": 0.5,
                "Water": 2,
                "Grass": 0.5,
                "Ground": 2,
                "Flying": 0.5,
                "Bug": 0.5,
                "Rock": 2,
                "Dragon": 0.5,
                "Steel": 0.5
            },
            "Ice": {
                "Fire": 0.5,
                "Water": 0.5,
                "Grass": 2,
                "Ice": 0.5,
                "Ground": 2,
                "Flying": 2,
                "Dragon": 2,
                "Steel": 0.5,
            },
            "Fighting": {
                "Normal": 2,
                "Ice": 2,
                "Rock": 2,
                "Dark": 2,
                "Steel": 2,
                "Poison": 0.5,
                "Flying": 0.5,
                "Psychic": 0.5,
                "Bug": 0.5,
                "Ghost": 0,
                "Fairy": 0.5,
            },
            "Poison": {
                "Grass": 2,
                "Fairy": 2,
                "Poison": 0.5,
                "Ground": 0.5,
                "Rock": 0.5,
                "Ghost": 0.5,
                "Steel": 0,
            },
            "Ground": {
                "Fire": 2,
                "Electric": 2,
                "Grass": 0.5,
                "Poison": 2,
                "Flying": 0,
                "Bug": 0.5,
                "Rock": 2,
                "Steel": 2,
            },
            "Flying": {
                "Grass": 2,
                "Electric": 0.5,
                "Fighting": 2,
                "Bug": 2,
                "Rock": 0.5,
                "Steel": 0.5,
            },
            "Psychic": {
                "Fighting": 2,
                "Poison": 2,
                "Psychic": 0.5,
                "Dark": 0,
                "Steel": 0.5,
            },
            "Bug": {
                "Grass": 2,
                "Fire": 0.5,
                "Fighting": 0.5,
                "Poison": 0.5,
                "Flying": 0.5,
                "Psychic": 2,
                "Ghost": 0.5,
                "Dark": 2,
                "Steel": 0.5,
                "Fairy": 0.5,
            },
            "Rock": {
                "Fire": 2,
                "Ice": 2,
                "Flying": 2,
                "Bug": 2,
                "Fighting": 0.5,
                "Ground": 0.5,
                "Steel": 0.5,
            },
            "Ghost": {
                "Normal": 0,
                "Psychic": 2,
                "Ghost": 2,
                "Dark": 0.5,
            },
            "Dragon": {
                "Dragon": 2,
                "Steel": 0.5,
                "Fairy": 0,
            },
            "Dark": {
                "Psychic": 2,
                "Ghost": 2,
                "Fighting": 0.5,
                "Dark": 0.5,
                "Fairy": 0.5,
            },
            "Steel": {
                "Fire": 0.5,
                "Water": 0.5,
                "Electric": 0.5,
                "Ice": 2,
                "Rock": 2,
                "Steel": 0.5,
                "Fairy": 2,
            },
            "Fairy": {
                "Fighting": 2,
                "Dragon": 2,
                "Dark": 2,
                "Fire": 0.5,
                "Poison": 0.5,
                "Steel": 0.5,
            },
        }

         # Initialize summary matrix
    
        attack_types = list(type_chart_attack.keys())
        effectiveness_levels = ["x2", "x1", "x0.5", "x0.25", "immunities"]

        # Initialize summary matrix
        summary_matrix = {t: {e: 0 for e in effectiveness_levels} for t in attack_types}

        # Individual attack factors for each Pokémon
        individual_attack = {t: [] for t in attack_types}

        for pokemon in self.team:
            # Pokemon with fairy type in generations below 6 must have their type changed to normal
            if self.gen_filter.currentIndex() < 6 and self.gen_filter.currentIndex() > 0 and (pokemon['Type1'] == 'Fairy' or pokemon['Type2']) == 'Fairy':
                if pokemon['Type1'] == 'Fairy':
                    pokemon['Type1'] = 'Normal'
                if pokemon['Type2'] == 'Fairy':
                    pokemon['Type2'] = ' '
            
            type1 = pokemon['Type1'].capitalize()
            type2 = pokemon['Type2'].capitalize() if pokemon['Type2'] != " " else None

            for attack_type in attack_types:
                factor1 = type_chart_attack.get(type1, {}).get(attack_type, 1)
                factor2 = type_chart_attack.get(type2, {}).get(attack_type, 1) if type2 else 1
                effectiveness = max(factor1, factor2)  # Take the most effective one

                # Add to individual attack
                individual_attack[attack_type].append(effectiveness)

                # Update summary matrix
                if effectiveness == 0:
                    summary_matrix[attack_type]["immunities"] += 1
                elif effectiveness == 4:
                    summary_matrix[attack_type]["x4"] += 1
                elif effectiveness == 2:
                    summary_matrix[attack_type]["x2"] += 1
                elif effectiveness == 1:
                    summary_matrix[attack_type]["x1"] += 1
                elif effectiveness == 0.5:
                    summary_matrix[attack_type]["x0.5"] += 1
                elif effectiveness == 0.25:
                    summary_matrix[attack_type]["x0.25"] += 1


        # Debug Print
        # print("Individual Attack:", individual_attack)
        # print("Summary Matrix:", summary_matrix)

        return individual_attack, summary_matrix, attack_types, effectiveness_levels
    
    def create_individual_attack_table(self, individual_attack, defend_types):
        pokemon_names = [pokemon['Name'] for pokemon in self.team]
        
        att_table = QTableWidget()
        att_table.setRowCount(len(defend_types))
        att_table.setColumnCount(len(pokemon_names))

        # Set headers
        att_table.setVerticalHeaderLabels(defend_types)
        att_table.setHorizontalHeaderLabels(pokemon_names)

        # Populate table
        for row, defend_type in enumerate(defend_types):
            for col, effectiveness in enumerate(individual_attack[defend_type]):
                item = QTableWidgetItem(f"{effectiveness:.2f}")
                item.setTextAlignment(Qt.AlignCenter)

                # Color coding
                if effectiveness == 0:
                    # Gray for immunity
                    item.setBackground(QColor(200, 200, 200))
                elif effectiveness == 2:
                    # Green for super effective
                    item.setBackground(QColor(150, 255, 150))
                elif effectiveness == 1:
                    # white
                    item.setBackground(QColor(255, 255, 255))
                elif effectiveness == 0.5:
                    # light red
                    item.setBackground(QColor(255, 150, 150))
                elif effectiveness == 0.25:
                    # red
                    item.setBackground(QColor(255, 100, 100))

                att_table.setItem(row, col, item)

        att_table.resizeColumnsToContents()
        att_table.resizeRowsToContents()
        att_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        att_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return att_table
    
    def create_summary_attack_table(self, summary_matrix, defend_types, effectiveness_levels):
        att_table = QTableWidget()
        att_table.setRowCount(len(defend_types))
        att_table.setColumnCount(len(effectiveness_levels))

        # Set headers
        att_table.setVerticalHeaderLabels(defend_types)
        att_table.setHorizontalHeaderLabels(effectiveness_levels)

        # Populate table
        for row, defend_type in enumerate(defend_types):
            for col, effectiveness in enumerate(effectiveness_levels):
                value = summary_matrix[defend_type][effectiveness]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                # Color coding
                if effectiveness == "x2" and value > 0:
                    # green
                    item.setBackground(QColor(150, 255, 150))
                elif effectiveness == "x1" and value > 0:
                    # white
                    item.setBackground(QColor(255, 255, 255))
                elif effectiveness == "x0.5" and value > 0:
                    # light red
                    item.setBackground(QColor(255, 150, 150))
                elif effectiveness == "x0.25" and value > 0:
                    # red
                    item.setBackground(QColor(255, 100, 100))
                elif effectiveness == "immunities" and value > 0:
                    # gray
                    item.setBackground(QColor(200, 200, 200))
                else:
                    item.setBackground(QColor(255, 255, 255))

                att_table.setItem(row, col, item)

        att_table.resizeColumnsToContents()
        att_table.resizeRowsToContents()
        att_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        att_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return att_table

    def analyze_missing_types(self):
        # Get the list of all types
        all_types = [
            "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
            "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
        ]

        all_types = set(type_colors.keys())
        
        team_types = set()
        for pokemon in self.team:
            team_types.add(pokemon['Type1'])
            if pd.notna(pokemon['Type2']):
                team_types.add(pokemon['Type2'])
        missing_types = all_types - team_types
        
        # Display the missing types
        if not hasattr(self, 'missing_types_widget'):
            self.missing_types_widget = QWidget()
            self.missing_types_widget.setLayout(QVBoxLayout())
            self.main_layout.addWidget(self.missing_types_widget)

        # Clear previous missing types
        layout = self.missing_types_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Display missing types
        missing_types_label = QLabel("Missing Types:")
        layout.addWidget(missing_types_label)

        # Concatenate missing types into a single string
        missing_types_text = "; ".join(
            [f'<span style="color:{type_colors.get(missing_type, "#000000")}">{missing_type}</span>' for missing_type in missing_types]
        )

        # Create a QLabel for the concatenated missing types
        missing_types_display = QLabel(f'<html>{missing_types_text}</html>')
        missing_types_display.setTextFormat(Qt.RichText)
        layout.addWidget(missing_types_display)

        self.missing_types_widget.setLayout(layout)

    def clear_analysis(self):
        # Clear the highlighting of the stats
        for i in range(self.team_layout.count()):
            widget = self.team_layout.itemAt(i).widget()
            if widget:
                stats_widget = widget.findChild(QWidget, "stats_widget")
                if stats_widget:
                    for child in stats_widget.children():
                        if isinstance(child, QLabel):
                            child.setStyleSheet("")
        
        # Remove the analysis tables (defense and offense and summary)
        layout = self.def_analysis_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        layout = self.atk_analysis_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Clear the analysis widget
        self.def_analysis_widget.setFixedHeight(0)
        self.atk_analysis_widget.setFixedHeight(0)

        # Clear the missing types widget
        layout = self.missing_types_widget.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.missing_types_widget.setFixedHeight(0)

####### Suggestions Section #######
    def generate_suggestions(self):        

        form_filter = [
            "Mega", 
            "Primal", 
            "Origin", 
            "Ultra", 
            "Dawn", 
            "Dusk", 
            "Crowned", 
            "Hero", 
            "Eternamax", 
            "Stellar"]       
        Legendary_ID_filter = [
            144,
            145,
            146,
            150,
            151,
            243,
            244,
            245,
            249,
            250,
            251,
            377,
            378,
            379,
            380,
            381,    
            382,
            383,
            384,
            386,
            480,
            481,
            482,
            483,
            484,
            485,
            486,
            487,
            488,
            489,
            490,
            491,
            492,
            493,
            494,
            638,
            639,
            640,
            641,
            642,
            643,
            644,
            645,
            646,
            647,
            648,
            649,
            716,
            717,
            718,
            772,
            773,
            785,
            786,
            787,
            788,
            789,
            790,
            791,
            792,
            800,
            888,
            889,
            890,
            891,
            892,
            894,
            895,
            896,
            897,
            898,
            905,
            1001,
            1002,
            1003,
            1004,
            1007,
            1008,
            1014,
            1015,
            1016,
            1017,
            1024,
        ]


                # Call the calculate_team_suggestions function with the required arguments

        # Get the required arguments
        gen_filter = self.gen_filter.currentText()
        defense_summary = self.analyze_defense()[1]  # Get the defense summary

        # print("Defense Summary:", defense_summary)  # Debug print statement

        form_filter = [
            "Mega", 
            "Primal", 
            "Origin", 
            "Ultra", 
            "Dawn", 
            "Dusk", 
            "Crowned", 
            "Hero", 
            "Eternamax", 
            "Stellar"]       
        Legendary_ID_filter = [
            144,
            145,
            146,
            150,
            151,
            243,
            244,
            245,
            249,
            250,
            251,
            377,
            378,
            379,
            380,
            381,    
            382,
            383,
            384,
            386,
            480,
            481,
            482,
            483,
            484,
            485,
            486,
            487,
            488,
            489,
            490,
            491,
            492,
            493,
            494,
            638,
            639,
            640,
            641,
            642,
            643,
            644,
            645,
            646,
            647,
            648,
            649,
            716,
            717,
            718,
            772,
            773,
            785,
            786,
            787,
            788,
            789,
            790,
            791,
            792,
            800,
            888,
            889,
            890,
            891,
            892,
            894,
            895,
            896,
            897,
            898,
            905,
            1001,
            1002,
            1003,
            1004,
            1007,
            1008,
            1014,
            1015,
            1016,
            1017,
            1024]

        def calculate_team_suggestions(team, filtered_data, defense_summary):           
            def calculate_defensive_score(pokemon, defense_summary):
                
                type_chart_defense = {
                    "Normal": {"Fighting": 2, "Ghost": 0},
                    "Fire": {
                        "Fire": 0.5,
                        "Water": 2,
                        "Grass": 0.5,
                        "Ice": 0.5,
                        "Ground": 2,
                        "Bug": 0.5,
                        "Rock": 2,
                        "Steel": 0.5,
                        "Fairy": 0.5,
                    },
                    "Water": {
                        "Fire": 0.5,
                        "Water": 0.5,
                        "Electric": 2,
                        "Grass": 2,
                        "Ice": 0.5,
                        "Steel": 0.5
                    },
                    "Electric": {
                        "Electric": 0.5,
                        "Ground": 2,
                        "Flying": 0.5,
                        "Steel": 0.5
                    },
                    "Grass": {
                        "Fire": 2,
                        "Water": 0.5,
                        "Electric": 0.5,
                        "Grass": 0.5,
                        "Ice": 2,
                        "Poison": 2,
                        "Ground": 0.5,
                        "Flying": 2,
                        "Bug": 2
                    },
                    "Ice": {
                        "Fire": 2,
                        "Ice": 0.5,
                        "Fighting": 2,
                        "Rock": 2,
                        "Steel": 2
                    },
                    "Fighting": {
                        "Flying": 2,
                        "Psychic": 2,
                        "Bug": 0.5,
                        "Rock": 0.5,
                        "Dark": 0.5,
                        "Fairy": 2
                    },
                    "Poison": {
                        "Grass": 0.5,
                        "Fighting": 0.5,
                        "Poison": 0.5,
                        "Ground": 2,
                        "Psychic": 2,
                        "Bug": 0.5,
                        "Fairy": 0.5
                    },
                    "Ground": {
                        "Water": 2,
                        "Electric": 0,
                        "Grass": 2,
                        "Ice": 2,
                        "Poison": 0.5,
                        "Rock": 0.5
                    },
                    "Flying": {
                        "Electric": 2,
                        "Ice": 2,
                        "Rock": 2,
                        "Grass": 0.5,
                        "Fighting": 0.5,
                        "Bug": 0.5,
                        "Ground": 0
                    },
                    "Psychic": {
                        "Fighting": 0.5,
                        "Psychic": 0.5,
                        "Bug": 2,
                        "Ghost": 2,
                        "Dark": 2
                    },
                    "Bug": {
                        "Fire": 2,
                        "Grass": 0.5,
                        "Fighting": 0.5,
                        "Ground": 0.5,
                        "Flying": 2,
                        "Rock": 2
                    },
                    "Rock": {
                        "Normal": 0.5,
                        "Fire": 0.5,
                        "Water": 2,
                        "Grass": 2,
                        "Fighting": 2,
                        "Poison": 0.5,
                        "Ground": 2,
                        "Flying": 0.5,
                        "Steel": 2
                    },
                    "Ghost": {
                        "Normal": 0,
                        "Fighting": 0,
                        "Poison": 0.5,
                        "Bug": 0.5,
                        "Ghost": 2,
                        "Dark": 2
                    },
                    "Dragon": {
                        "Fire": 0.5,
                        "Water": 0.5,
                        "Grass": 0.5,
                        "Electric": 0.5,
                        "Ice": 2,
                        "Dragon": 2,
                        "Fairy": 2
                    },
                    "Dark": {
                        "Fighting": 2,
                        "Psychic": 0,
                        "Bug": 2,
                        "Ghost": 0.5,
                        "Dark": 0.5,
                        "Fairy": 2
                    },
                    "Steel": {
                        "Normal": 0.5,
                        "Fire": 2,
                        "Grass": 0.5,
                        "Ice": 0.5,
                        "Fighting": 2,
                        "Poison": 0,
                        "Ground": 2,
                        "Flying": 0.5,
                        "Psychic": 0.5,
                        "Bug": 0.5,
                        "Rock": 0.5,
                        "Dragon": 0.5,
                        "Steel": 0.5,
                        "Fairy": 0.5
                    },
                    "Fairy": {
                        "Fighting": 0.5,
                        "Poison": 2,
                        "Bug": 0.5,
                        "Dragon": 0,
                        "Dark": 0.5,
                        "Steel": 2
                    }
                }

                score = 0
                pokemon_types = [pokemon['Type1'], pokemon['Type2']]

                # Get the types of the Pokémon in the team
                team_types = set()
                for team_pokemon in team:
                    team_types.add(team_pokemon['Type1'])
                    if team_pokemon['Type2'] != " ":
                        team_types.add(team_pokemon['Type2'])

                for defending_type, effectiveness_dict in defense_summary.items():
                    for effectiveness, count in effectiveness_dict.items():
                        if effectiveness in ['x2', 'x4'] and count > 0:  # x2 or x4 effective against the team
                            # Check if the team already has a resistance to this vulnerability
                            has_resistance = False
                            for team_type in team_types:
                                if team_type in type_chart_defense:
                                    resistance = type_chart_defense[team_type].get(defending_type, 1)
                                    if resistance <= 0.25:  # Resistance or immunity
                                        has_resistance = True
                                        break
                            
                            if not has_resistance:
                                for pokemon_type in pokemon_types:
                                    if pokemon_type in type_chart_defense:
                                        resistance = type_chart_defense[pokemon_type].get(defending_type, 1)
                                        if resistance == 0:
                                            score += 35  # Higher score for immunity
                                        elif resistance <= 0.25:
                                            score += 25  # Score for resistance
                                        elif resistance <= 0.5:
                                            score += 15
                return score

            def threshold(stat):
                thresholds = {
                    'HP': 65,
                    'Attack': 80,
                    'Defense': 80,
                    'Sp. Atk': 80,
                    'Sp. Def': 80,
                    'Speed': 80
                }
                return thresholds[stat]   

            def guess_role(pokemon):
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
                roles = []
                for member in team:
                    roles.append(guess_role(member))
                return roles
            
            # Implement your logic to calculate team suggestions here
            print(f"Calculating team suggestions with gen_filter: {gen_filter}")

            suggestions = []

            team_names_with_forms = [f"{member['Name']} ({member.get('Form', '')})" if member.get('Form') else member['Name'] for member in team]
            
            # Example: Clear previous suggestions
            suggestions.clear()

            # Initialize compatibility score for the Pokémon
            score = 0

            for _, pokemon in filtered_data.iterrows():
                current_name = f"{pokemon['Name']} ({pokemon.get('Form', '')})" if pokemon.get('Form') else pokemon['Name']
                if current_name in team_names_with_forms:
                    continue

                score = calculate_defensive_score(pokemon, defense_summary)
                has_above_threshold = False

                for stat in ['HP', 'Attack', 'Sp. Atk', 'Defense', 'Sp. Def', 'Speed']:
                    pokemon_stat = pokemon[stat]
                    stat_threshold = threshold(stat)
                    if pokemon_stat > stat_threshold:
                        has_above_threshold = True
                        score += ((pokemon_stat - stat_threshold) / stat_threshold)*10
                        # print(f"added {((pokemon_stat - stat_threshold) / stat_threshold)*10} to score")
                        # print(f"score of pokemon {pokemon['Name']} is {score}")

                if not has_above_threshold:
                    score -= 20  # Penalize for not meeting any threshold

                # Missing Roles
                guessed_role = guess_role(pokemon)
                team_roles = identify_team_roles(team)
                if guessed_role not in team_roles and guessed_role != 'Generalist':
                    score += 20  # Reward for filling missing roles

                # multiple mixed sweepers is not a problem
                if guessed_role == 'Mixed Sweeper' and team_roles.count('Mixed Sweeper') >= 1:
                    score += 10

                # Typing Synergy
                team_types = [member['Type1'] for member in team] + [member['Type2'] for member in team if member['Type2'] != " "]
                if pokemon.get('Type1') not in team_types:
                    score += 15  # Small reward for introducing new types
                if pokemon.get('Type2') != " " and pokemon.get('Type2') not in team_types:
                    score += 15

                # 4. Flexibility
                # dual_roles = calculate_flexibility(filtered_data)  # Some method to assess role versatility
                # score += dual_roles * 2  # Higher weight for dual-role capability

                # BST Ordering
                bst = pokemon.get('Total', 0)
                score += bst / 100  # Normalize BST influence

                # Append Pokémon with form consideration
                name = pokemon['Name']
                form = pokemon.get('Form', ' ')
                suggestions.append({'name': name, 'form': form, 'role': guessed_role ,'score': score})
                
                        
            # Sort suggestions by score in descending order
            sorted_suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)

            # print(f"Top 18 suggestions: {sorted_suggestions[:18]}")
            return sorted_suggestions[:18]  # Return top 18 Pokémon
        
        # Apply the same filtering logic
        self.filtered_data = self.pokemon_data.copy()

        # Filter Pokémon by generation
        gen_index = self.gen_filter.currentIndex()
        if gen_index > 0:
            self.filtered_data = self.filtered_data[self.filtered_data['Generation'] <= gen_index]

        # Adjust Fairy type for generations below 6
        if gen_index < 6:
            self.filtered_data.loc[self.filtered_data['Type1'] == 'Fairy', 'Type1'] = 'Normal'
            self.filtered_data.loc[self.filtered_data['Type2'] == 'Fairy', 'Type2'] = 'Normal'

        # Filter Pokémon by mega evolution and special forms
        if not self.mega_filter.isChecked():
            self.filtered_data = self.filtered_data[~self.filtered_data['Form'].str.contains('|'.join(form_filter))]

        # Filter Pokémon by legendaries if the column exists
        if not self.legendary_filter.isChecked():
            self.filtered_data = self.filtered_data[~self.filtered_data['ID'].isin(Legendary_ID_filter)]

        # Filter Pokémon by type
        type_filter = self.type_filter.currentText()
        if type_filter != "All Types":
            self.filtered_data = self.filtered_data[
                (self.filtered_data['Type1'] == type_filter) | (self.filtered_data['Type2'] == type_filter)
            ]

        # remove Pokemon with "Total" < 350
        self.filtered_data = self.filtered_data[self.filtered_data['Total'] >= 350]

        suggestions = calculate_team_suggestions(self.team, self.filtered_data, defense_summary)

        # Display the suggestions
        self.display_suggestions(suggestions)
    
    def display_suggestions(self, suggestions):
            def get_random_image_path(pokemon_id, name, form):
                base_folder = r"./data/pokemon_images"
                
                form_suffix = f"-{form}" if form != " " else ""

                pattern = f"{base_folder}/{pokemon_id}_*_{name}{form_suffix}.png"
                matching_files = glob.glob(pattern)
                # print(pattern)
                if matching_files:
                    return random.choice(matching_files)
                # If no images are found, return a placeholder image
                return "./data/misc_images/substitute.png"

            self.clear_suggestions()

            # Add new suggestions
            for i, suggestion in enumerate(suggestions):
                name = suggestion['name']
                form = suggestion['form']
                score = suggestion['score']
                score = round(score, 2)

                pokemon = self.pokemon_data[(self.pokemon_data['Name'] == name) & (self.pokemon_data['Form'] == form)].iloc[0]
                types = f"{pokemon['Type1']}/{pokemon['Type2']}" if pokemon["Type2"] != " " else pokemon['Type1']
                bst_total = pokemon[['Total']].values[0]
                role = suggestion['role']

                # Conditionally add parentheses around the form if it exists
                form_text = f" ({form})" if form != " " else ""

                # Get a random image path
                image_path = get_random_image_path(pokemon['ID'], name, form)

                # Create a label for the suggestion
                suggestion_label = QLabel(f"Name: {name} {form_text}\nTypes: {types}\nBST: {bst_total}\nRole: {role}\nScore: {score}")

                # Create an image label
                image_label = QLabel()
                if image_path:
                    pixmap = QPixmap(image_path)
                    image_label.setPixmap(pixmap)

                # Create a vertical layout for each Pokémon
                vbox = QVBoxLayout()
                vbox.addWidget(image_label)
                vbox.addWidget(suggestion_label)

                # Add the vertical layout to the grid layout
                self.suggestions_layout.addLayout(vbox, i // 9, i % 9)

                # print(f"Added suggestion {name} to the grid layout")

            # Set the grid layout to the suggestions widget
            self.suggestions_widget.setFixedHeight(600)
            self.suggestions_widget.update()

    def clear_suggestions(self):
        # Clear previous suggestions
        layout = self.suggestions_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
            layout.removeItem(item)
        self.suggestions_widget.update()  # Explicitly update the widget

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
            layout.removeItem(item)
            
####### PC Box Team Builder Section #######

    def PC_Box_update_autofill(self):
        self.PC_box_pokemon_data = self.pokemon_data.copy()

        query = self.PC_Box_search_entry.text().strip().lower()

        if query:
            try:
                PC_box_pokemon_data = self.pokemon_data[
                    self.pokemon_data['Name'].str.lower().str.contains(query, na=False) |
                    self.pokemon_data['Form'].str.lower().str.contains(query, na=False)
                ]
            
            except re.error:
                print(f"Error in filtering: {re.error}")
                PC_box_pokemon_data = pd.DataFrame()

        else:
            PC_box_pokemon_data = self.pokemon_data.copy()


       # Filter Pokémon by generation
        gen_index = self.gen_filter.currentIndex()
        if gen_index > 0:
            PC_box_pokemon_data = PC_box_pokemon_data[PC_box_pokemon_data['Generation'] <= gen_index]

        # Adjust Fairy type for generations below 6
        if gen_index < 6 and gen_index > 0:
            PC_box_pokemon_data.loc[PC_box_pokemon_data['Type1'] == 'Fairy', 'Type1'] = 'Normal'
            PC_box_pokemon_data.loc[PC_box_pokemon_data['Type2'] == 'Fairy', 'Type2'] = ' '

        # Update the autofill box with the filtered Pokémon
        self.PC_box_pokemon_data = PC_box_pokemon_data
        self.PC_Box_autofill_box.clear()
        for _, pokemon in PC_box_pokemon_data.iterrows():
            self.PC_Box_autofill_box.addItem(pokemon['Name'])

        ##
        self.PC_Box_populate_autofill_box(self.PC_box_pokemon_data.head(5)) 

    def PC_Box_populate_autofill_box(self, PC_box_pokemon_data):
        self.PC_Box_autofill_box.clear()  # Clear existing items
        max_items = 5  # Maximum number of items to display
        item_height = 30  # Adjust this value based on your item height
        for _, pokemon in PC_box_pokemon_data.iterrows():
            form_suffix = f" ({pokemon['Form'].strip()})" if pokemon['Form'] != " " else ""
            if pokemon["Form"] != " ":
                self.PC_Box_autofill_box.addItem(f"{pokemon['Name']}{form_suffix}")
            else:
                self.PC_Box_autofill_box.addItem(f"{pokemon['Name']}")

        # Adjust height to show max_items
        self.PC_Box_autofill_box.setFixedHeight(min(len(PC_box_pokemon_data), max_items) * item_height)

    def PC_Box_add_autofill(self):
        print("add_autofill_to_team called")  # Debug print statement
        if self.adding_pokemon:
            # print("Already adding a Pokémon, skipping...")  # Debug print statement
            return  # Prevent multiple additions

        self.adding_pokemon = True  # Set the flag to prevent multiple additions
        # Check if the team is already full

        try:
            # Get the selected item from the autofill box
            current_item = self.PC_Box_autofill_box.currentItem()
            if not current_item:
                print("No item selected")  # Debug print statement
                return  # No item selected

            # Extract the full name including the form from the list
            selected_name = current_item.text()
            print(f"Selected name: {selected_name}")  # Debug print statement

            name, form = (selected_name.split(" (")[0].strip(),
                  selected_name.split(" (")[1].rstrip(")") if " (" in selected_name else "")

            # Match the Pokémon in the dataset
            selected_pokemon = self.pokemon_data[
                (self.pokemon_data['Name'] == name) & (self.pokemon_data['Form'].str.strip() == form)
            ]

            if not selected_pokemon.empty:
                pokemon_dict = selected_pokemon.iloc[0].to_dict()
                self.add_autofill_to_Box(pokemon_dict)
                self.PC_Box_update_autofill()
                self.adding_pokemon = False  # Reset the flag

        except Exception as e:
            print(f"Error adding autofill to team: {e}")

    def add_autofill_to_Box(self, pokemon_data):
         # Add Pokémon to the PC-Box
        key = f"{pokemon_data['Name']} {pokemon_data['Form']}".strip()
        self.pc_box[key] = pokemon_data
        self.pc_box_list.append(key)
        self.display_pokemon_in_box()

    def display_pokemon_in_box(self):
        def get_random_image_path(pokemon_id, name, form):
            base_folder = r"./data/pokemon_images"
            
            form_suffix = f"-{form}" if form != " " else ""

            pattern = f"{base_folder}/{pokemon_id}_*_{name}{form_suffix}.png"
            matching_files = glob.glob(pattern)
            # print(pattern)
            if matching_files:
                return random.choice(matching_files)
            # If no images are found, return a placeholder image
            return "./data/misc_images/substitute.png"
        
        def remove_pokemon_from_box(index):
            if 0 <= index < len(self.pc_box_list):
                pokemon_name = self.pc_box_list[index]
                del self.pc_box[pokemon_name]
                self.pc_box_list.pop(index)
                self.display_pokemon_in_box()

        # Safely clear the current layout
        while self.PC_Box_layout.count():
            child = self.PC_Box_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

        max_pokemon = 42
        display_pokemon = self.pc_box_list[:max_pokemon]

        # Display Pokémon in a grid (e.g., 7 columns per row)
        print(f"Displaying Pokémon in the PC Box: {display_pokemon}")
        for index, pokemon_name in enumerate(display_pokemon):
            pokemon = self.pc_box[pokemon_name.strip()]
            if not pokemon:
                continue
            name = pokemon['Name']
            form = pokemon['Form']

            # Check gen filter for Fairy type
            gen_index = self.PC_Box_gen_filter.currentIndex()
            if gen_index < 6 and gen_index > 0:
                if pokemon['Type1'] == 'Fairy':
                    pokemon['Type1'] = 'Normal'
                if pokemon['Type2'] == 'Fairy':
                    pokemon['Type2'] = ' '
                    
            types = f"{pokemon['Type1']}/{pokemon['Type2']}" if pokemon["Type2"] != " " else pokemon['Type1']
            bst_total = pokemon['Total']

            # Create a label for the Pokémon
            pokemon_label = QLabel(f"Name: {name} {form}\nTypes: {types}\nBST: {bst_total}")

            image_label = QLabel()
            image_path = get_random_image_path(pokemon['ID'], name, form)
            pixmap = QPixmap(image_path)

            if not pixmap.isNull():  # Check if the image exists
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image not found")

            # Create a button to remove the Pokémon
            remove_button = QPushButton("Remove")
            remove_button.setFixedWidth(100)
            remove_button.clicked.connect(lambda _, idx=index: remove_pokemon_from_box(idx))

            # Create Pokémon display widgets
            # print(f"Adding Pokémon to the PC Box: {name} {form}")
            vbox = QVBoxLayout()
            vbox.addWidget(image_label)
            vbox.addWidget(pokemon_label)
            vbox.addWidget(remove_button)

            container_widget = QWidget()
            container_widget.setLayout(vbox)
            container_widget.setFixedSize(self.PC_Box_Widget.width() // 7, 150)
            container_widget.setMaximumSize(200, 300) 

            # Calculate grid position
            row, col = divmod(index, 7)
            self.PC_Box_layout.addWidget(container_widget, row, col)
            # print(f"Added Pokémon to the PC Box: {name} {form} at row {row}, col {col}")
       
    def PC_Box_build_team(self):       
        def calculate_team_suggestions(pc_box, pokemon_data, defense_analysis):
            def calculate_team_score(team):
                score = 0
                
                def guess_role(pokemon):
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

                def calculate_defensive_score(pokemon, defense_summary):
                    type_chart_defense = {
                        "Normal": {"Fighting": 2, "Ghost": 0},
                        "Fire": {
                            "Fire": 0.5,
                            "Water": 2,
                            "Grass": 0.5,
                            "Ice": 0.5,
                            "Ground": 2,
                            "Bug": 0.5,
                            "Rock": 2,
                            "Steel": 0.5,
                            "Fairy": 0.5,
                        },
                        "Water": {
                            "Fire": 0.5,
                            "Water": 0.5,
                            "Electric": 2,
                            "Grass": 2,
                            "Ice": 0.5,
                            "Steel": 0.5
                        },
                        "Electric": {
                            "Electric": 0.5,
                            "Ground": 2,
                            "Flying": 0.5,
                            "Steel": 0.5
                        },
                        "Grass": {
                            "Fire": 2,
                            "Water": 0.5,
                            "Electric": 0.5,
                            "Grass": 0.5,
                            "Ice": 2,
                            "Poison": 2,
                            "Ground": 0.5,
                            "Flying": 2,
                            "Bug": 2
                        },
                        "Ice": {
                            "Fire": 2,
                            "Ice": 0.5,
                            "Fighting": 2,
                            "Rock": 2,
                            "Steel": 2
                        },
                        "Fighting": {
                            "Flying": 2,
                            "Psychic": 2,
                            "Bug": 0.5,
                            "Rock": 0.5,
                            "Dark": 0.5,
                            "Fairy": 2
                        },
                        "Poison": {
                            "Grass": 0.5,
                            "Fighting": 0.5,
                            "Poison": 0.5,
                            "Ground": 2,
                            "Psychic": 2,
                            "Bug": 0.5,
                            "Fairy": 0.5
                        },
                        "Ground": {
                            "Water": 2,
                            "Electric": 0,
                            "Grass": 2,
                            "Ice": 2,
                            "Poison": 0.5,
                            "Rock": 0.5
                        },
                        "Flying": {
                            "Electric": 2,
                            "Ice": 2,
                            "Rock": 2,
                            "Grass": 0.5,
                            "Fighting": 0.5,
                            "Bug": 0.5,
                            "Ground": 0
                        },
                        "Psychic": {
                            "Fighting": 0.5,
                            "Psychic": 0.5,
                            "Bug": 2,
                            "Ghost": 2,
                            "Dark": 2
                        },
                        "Bug": {
                            "Fire": 2,
                            "Grass": 0.5,
                            "Fighting": 0.5,
                            "Ground": 0.5,
                            "Flying": 2,
                            "Rock": 2
                        },
                        "Rock": {
                            "Normal": 0.5,
                            "Fire": 0.5,
                            "Water": 2,
                            "Grass": 2,
                            "Fighting": 2,
                            "Poison": 0.5,
                            "Ground": 2,
                            "Flying": 0.5,
                            "Steel": 2
                        },
                        "Ghost": {
                            "Normal": 0,
                            "Fighting": 0,
                            "Poison": 0.5,
                            "Bug": 0.5,
                            "Ghost": 2,
                            "Dark": 2
                        },
                        "Dragon": {
                            "Fire": 0.5,
                            "Water": 0.5,
                            "Grass": 0.5,
                            "Electric": 0.5,
                            "Ice": 2,
                            "Dragon": 2,
                            "Fairy": 2
                        },
                        "Dark": {
                            "Fighting": 2,
                            "Psychic": 0,
                            "Bug": 2,
                            "Ghost": 0.5,
                            "Dark": 0.5,
                            "Fairy": 2
                        },
                        "Steel": {
                            "Normal": 0.5,
                            "Fire": 2,
                            "Grass": 0.5,
                            "Ice": 0.5,
                            "Fighting": 2,
                            "Poison": 0,
                            "Ground": 2,
                            "Flying": 0.5,
                            "Psychic": 0.5,
                            "Bug": 0.5,
                            "Rock": 0.5,
                            "Dragon": 0.5,
                            "Steel": 0.5,
                            "Fairy": 0.5
                        },
                        "Fairy": {
                            "Fighting": 0.5,
                            "Poison": 2,
                            "Bug": 0.5,
                            "Dragon": 0,
                            "Dark": 0.5,
                            "Steel": 2
                        }
                    }

                    def_score = 0
                    pokemon_types = [pokemon['Type1'], pokemon['Type2']]

                    # Get the types of the Pokémon in the team
                    team_types = set()
                    for team_pokemon in team:
                        team_types.add(team_pokemon['Type1'])
                        if team_pokemon['Type2'] != " ":
                            team_types.add(team_pokemon['Type2'])

                    for defending_type, effectiveness_dict in defense_summary.items():
                        for effectiveness, count in effectiveness_dict.items():
                            if effectiveness in ['x2', 'x4'] and count > 0:  # x2 or x4 effective against the team
                                # Check if the team already has a resistance to this vulnerability
                                has_resistance = False
                                for team_type in team_types:
                                    if team_type in type_chart_defense:
                                        resistance = type_chart_defense[team_type].get(defending_type, 1)
                                        if resistance <= 0.25:  # Resistance or immunity
                                            has_resistance = True
                                            break
                                
                                if not has_resistance:
                                    for pokemon_type in pokemon_types:
                                        if pokemon_type in type_chart_defense:
                                            resistance = type_chart_defense[pokemon_type].get(defending_type, 1)
                                            if resistance == 0:
                                                def_score += 35  # Higher score for immunity
                                            elif resistance <= 0.25:
                                                def_score += 25  # Score for resistance
                                            elif resistance <= 0.5:
                                                def_score += 15
                    return def_score

                def threshold(stat):
                    thresholds = {
                        'HP': 65,
                        'Attack': 80,
                        'Defense': 80,
                        'Sp. Atk': 80,
                        'Sp. Def': 80,
                        'Speed': 80
                    }
                    return thresholds[stat]   

                # Score based on the number of types in the team
                team_types = set()
                for pokemon in team:
                    team_types.add(pokemon['Type1'])
                    if pokemon['Type2'] != " ":
                        team_types.add(pokemon['Type2'])
                score += len(team_types) * 10

                # Score based on the number of unique roles in the team
                roles = [guess_role(pokemon) for pokemon in team]
                unique_roles = set()
                mixed_sweepers_count = 0
                for role in roles:
                    if role == 'Mixed Sweeper':
                        mixed_sweepers_count += 1
                    else:
                        unique_roles.add(role)
                
                if mixed_sweepers_count > 0:
                    if 'Physical Sweeper' not in unique_roles:
                        unique_roles.add('Physical Sweeper')
                    if 'Special Sweeper' not in unique_roles:
                        unique_roles.add('Special Sweeper')

                score += len(unique_roles) * 10

                # Score based on the number of dual-role Pokémon (it can be a sweeper and a wall)
                dual_role_count = 0
                for pokemon in team:
                    role = guess_role(pokemon)
                    if role in ['Physical Sweeper', 'Special Sweeper', 'Mixed Sweeper']:
                        if pokemon['Defense'] >= 100 or pokemon['Sp. Def'] >= 100 or (pokemon['Defense'] >= 80 and pokemon['HP'] >= 80) or (pokemon['Sp. Def'] >= 80 and pokemon['HP'] >= 80):
                            dual_role_count += 1
                score += dual_role_count * 15

                # Score based on the number of Pokémon with above-threshold stats
                for pokemon in team:
                    for stat in ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']:
                        if pokemon[stat] >= threshold(stat):
                            score += (pokemon[stat] - threshold(stat))/10

                # Calculate the defensive score
                for pokemon in team:
                    defense_score = calculate_defensive_score(pokemon, defense_analysis)

                return score

            best_team = None
            best_score = -float('inf')

            # Generate all possible combinations of 6 Pokémon
            for team_combination in combinations(pc_box, 6):
                team_score = calculate_team_score(team_combination)
                if team_score > best_score:
                    best_score = team_score
                    best_team = team_combination

            # Ensure the function always returns a valid tuple
            if best_team is None:
                best_team = []
                best_score = 0

            return best_team, best_score

         # Get all Pokémon in the PC Box
        
        PC_Box = [self.pc_box[pokemon_name] for pokemon_name in self.pc_box.keys()]
        best_team, best_score = calculate_team_suggestions(PC_Box, self.PC_box_pokemon_data, self.analyze_defense()[1])

        # Display the best team in PC_Box_Team_suggestions_widget with the score of the team with images
        self.PC_Box_display_best_team(best_team, best_score)
    
    def PC_Box_display_best_team(self, best_team, best_score):
            def get_random_image_path(pokemon_id, name, form):
            
                base_folder = r"./data/pokemon_images"
                
                form_suffix = f"-{form}" if form != " " else ""

                pattern = f"{base_folder}/{pokemon_id}_*_{name}{form_suffix}.png"
                matching_files = glob.glob(pattern)
                # print(pattern)
                if matching_files:
                    return random.choice(matching_files)
                # If no images are found, return a placeholder image
                return "./data/misc_images/substitute.png"
            
            def guess_role(pokemon):
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

            while self.PC_Box_Team_suggestions_layout.count():
                child = self.PC_Box_Team_suggestions_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())

            # Display the best team
            for index, pokemon in enumerate(best_team):
                name = pokemon['Name']
                form = pokemon['Form']
                types = f"{pokemon['Type1']}/{pokemon['Type2']}" if pokemon["Type2"] != " " else pokemon['Type1']
                bst_total = pokemon['Total']
                role = guess_role(pokemon)

                # Create a label for the Pokémon
                # Form in parentheses if it exists
                # change types to type if only 1 type
                if pokemon["Type2"] != " ":
                    if pokemon["Form"] != " ":
                        pokemon_label = QLabel(f"Name: {name} ({form})\nTypes: {types}\nBST: {bst_total}\nRole: {role}")
                    else:
                        pokemon_label = QLabel(f"Name: {name}\nTypes: {types}\nBST: {bst_total}\nRole: {role}")
                else:
                    if pokemon["Form"] != " ":
                        pokemon_label = QLabel(f"Name: {name} ({form})\nType: {types}\nBST: {bst_total}\nRole: {role}")
                    else:
                        pokemon_label = QLabel(f"Name: {name}\nType: {types}\nBST: {bst_total}\nRole: {role}")


                image_label = QLabel()
                image_path = get_random_image_path(pokemon['ID'], name, form)
                pixmap = QPixmap(image_path)

                if not pixmap.isNull():  # Check if the image exists
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(pixmap)
                else:
                    image_label.setText("Image not found")

                # Create Pokémon display widgets
                print(f"Adding Pokémon to the PC Box: {name} {form}")
                vbox = QVBoxLayout()
                vbox.addWidget(image_label)
                vbox.addWidget(pokemon_label)

                # Calculate grid position
                row, col = divmod(index, 7)
                self.PC_Box_Team_suggestions_layout.addLayout(vbox, row, col)
                print(f"Added Pokémon to the PC Box: {name} {form} at row {row}, col {col}")

            # Display the best score
            score_label = QLabel(f"Best Team Score: {best_score}")
            self.PC_Box_Team_suggestions_layout.addWidget(score_label)
            self.PC_Box_Team_suggestions_layout.setAlignment(score_label, Qt.AlignCenter)
        
    def PC_Box_clear_team(self):
        # Clear the PC Box Widget with all the pokemons inside
        self.pc_box = {}
        self.pc_box_list.clear()
        self.display_pokemon_in_box()

    def clear_box_team(self):
        # Clear the PC Box
        self.pc_box = {}
        self.pc_box_list.clear()
        self.pc_box_list_widget.clear()
        self.display_pokemon_in_box(self.pc_box_list)


def main():
    app = QApplication(sys.argv)
    pokemon_data = pd.read_csv('./data/Pokemon.csv')
    optimizer = PokemonTeamOptimizer(pokemon_data)
    optimizer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

