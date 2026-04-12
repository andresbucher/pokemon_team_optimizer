import json
import sys
from pathlib import Path
import pandas as pd


def _resource_base_path():
    """Return the root folder that contains the data directory."""
    # PyInstaller extracts bundled files to _MEIPASS at runtime.
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def _data_path(*parts):
    return _resource_base_path() / 'data' / Path(*parts)

def load_pokemon_data():
    """Load Pokemon data from CSV file"""
    return pd.read_csv(_data_path('Pokemon.csv'))

def load_json_data(filename):
    """Load JSON data from file"""
    with open(_data_path('json', f'{filename}.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def get_type_colors():
    """Get type colors dictionary"""
    return load_json_data('type_colors')

def get_form_filters():
    """Get form filters list"""
    return load_json_data('form_filters')

def get_legendary_ids():
    """Get legendary Pokemon IDs list"""
    return load_json_data('legendary_ids')

def get_type_chart():
    """Get type effectiveness chart"""
    return load_json_data('type_chart')