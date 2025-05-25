# Pokemon Team Optimizer

A basic tool for optimizing Pokemon teams with analysis, filtering, and suggestions.

## Features

- **Team Builder**: Create and analyze your team
  - Interface to create teams of up to 6 Pokemon
  - Search and filter Pokemon by name, type and stats
  - Save and load multiple team configurations (still in work)

- **PC Box**: Store multiple Pokemon for team building
  - Store and organize Pokemon for easy team building
  - Save and load Boxes (still in work)

- **Team Analysis**: 
  - **Defense Analysis**: Evaluate team weaknesses and resistances to all types
  - **Attack Analysis**: Calculate offensive coverage
  - **Type Coverage Analysis**: Identify types your team struggles against
  - **Stat Distribution**: Visualize your team's stat spread and identify imbalance

- **Team Suggestions**: Get suggestions for improving your team
  - Identify and fix type coverage gaps
  - Alternate Pokemon suggestions that better fit your strategy based on a arbitrary score trying to get offensive, defensive and "Team-Role" (Physical Attacker, Special sweeper, Walls etc.) without including their Movepool and/or Abilitie as it's really hard to give a score to the huge movepool and abilities?

## Installation

1. Clone the repository:
```bash
git clone https://github.com/andresbucher/pokemon_team_optimizer.git
cd pokemon_team_optimizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Basic Team Building
1. Launch the application using `python main.py`
2. Click "New Team" to create a team (still in work)
3. Use the search function to find Pokemon
4. Click on a Pokemon to view details and add to your team (still in work)
5. Save your team using File > Save Team

### Team Analysis
1. With a team loaded, click on "Analysis" in the main menu
2. Select the type of analysis you want to perform
3. Review the charts and suggestions provided
4. Make adjustments to your team based on the analysis

### Team Suggestions
1. Navigate to the "Suggestions" tab
2. The system will highlight weaknesses in your current team (still in work)
3. Browse through suggested Pokemon to address these weaknesses

## Requirements

```
pandas==1.3.5
PyQt5==5.15.4
beautifulsoup4==4.10.0
requests==2.27.1
```

## Project Structure

```
pokemon_team_optimizer/
├── main.py              # Application entry point
├── pokemon/             # Pokemon data and models
├── analysis/            # Team analysis algorithms
├── ui/                  # User interface components
├── data/                # Pokemon database and resources
└── utils/               # Helper functions and utilities
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
Pokemon data sourced from PokeAPI ()
Type effectiveness calculations based on official Pokemon game mechanics