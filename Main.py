import sys
from PyQt5.QtWidgets import QApplication

from src.utils.data_loader import load_pokemon_data
from src.ui.main_window import PokemonTeamOptimizer

def main():
    app = QApplication(sys.argv)
    pokemon_data = load_pokemon_data()
    optimizer = PokemonTeamOptimizer(pokemon_data)
    optimizer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()