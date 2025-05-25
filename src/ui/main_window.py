import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QHBoxLayout, QComboBox, QCheckBox, QLineEdit,
    QScrollArea, QSizePolicy, QListWidget, QTableWidget, QGridLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..utils.data_loader import (
    load_pokemon_data, get_type_colors, get_form_filters, get_legendary_ids
)
from ..utils.image_handler import get_image_path
from ..logic.team_analysis import analyze_defense, analyze_attack, analyze_missing_types
from ..logic.suggestions import generate_team_suggestions
from ..logic.role_detection import guess_role
from .styles import stylesheet
from .team_builder_tab import TeamBuilderTab
from .pc_widget_tab import PCWidgetTab

class PokemonTeamOptimizer(QMainWindow):
    """Main application window for Pokemon Team Optimizer."""
    
    def __init__(self, pokemon_data):
        super().__init__()
        self.pokemon_data = pokemon_data
        
        # Load data
        self.pokemon_data = load_pokemon_data()
        self.type_colors = get_type_colors()
        self.form_filter = get_form_filters()
        self.legendary_ids = get_legendary_ids()
        
        # Initialize state
        self.team = []
        self.pc_box = {}
        self.pc_box_list = []
        self.filtered_data = self.pokemon_data.copy()
        self.adding_pokemon = False
        
        # Set up UI
        self.setWindowTitle("Pokemon Team Optimizer")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(stylesheet)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.team_builder_tab = TeamBuilderTab(self)
        self.pc_box_tab = PCWidgetTab(self)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.team_builder_tab, "Team Builder")
        self.tab_widget.addTab(self.pc_box_tab, "PC Box")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Initialize the UI
        self.initialize_ui()
    
    def initialize_ui(self):
        """Initialize UI components and state."""
        self.team_builder_tab.initialize_ui()
        self.pc_box_tab.initialize_ui()
    
    def apply_filters(self):
        self.filtered_data = self.pokemon_data.copy()
        
        # Filter Pokémon by generation
        gen_index = self.team_builder_tab.gen_filter.currentIndex()
        if gen_index > 0:
            self.filtered_data = self.filtered_data[self.filtered_data['Generation'] <= gen_index]
            
        # Adjust Fairy type for generations below 6
        if gen_index < 6 and gen_index > 0:
            self.filtered_data.loc[self.filtered_data['Type1'] == 'Fairy', 'Type1'] = 'Normal'
            self.filtered_data.loc[self.filtered_data['Type2'] == 'Fairy', 'Type2'] = 'Normal'
            
        # Filter Pokémon by mega evolution and special forms
        if not self.team_builder_tab.mega_filter.isChecked():  # ← FIXED THIS LINE
            self.filtered_data = self.filtered_data[~self.filtered_data['Form'].str.contains('|'.join(self.form_filter))]
            
        # Filter Pokémon by legendaries
        if not self.team_builder_tab.legendary_filter.isChecked():  # ← CHECK THIS LINE TOO
            self.filtered_data = self.filtered_data[~self.filtered_data['ID'].isin(self.legendary_ids)]
            
        # Filter Pokémon by type
        type_filter = self.team_builder_tab.type_filter.currentText()  # ← AND THIS LINE
        if type_filter != "All Types":
            self.filtered_data = self.filtered_data[
                (self.filtered_data['Type1'] == type_filter) | (self.filtered_data['Type2'] == type_filter)
            ]
            
        # Filter by minimum base stat total
        self.filtered_data = self.filtered_data[self.filtered_data['Total'] >= 350]
        
        # Update UI components that depend on filtered data
        self.team_builder_tab.update_autofill()
        self.pc_box_tab.update_autofill()