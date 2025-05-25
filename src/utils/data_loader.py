import os
import json
import pandas as pd

def load_pokemon_data():
    """Load Pokemon data from CSV file"""
    return pd.read_csv('./data/Pokemon.csv')

def load_json_data(filename):
    """Load JSON data from file"""
    with open(f'./data/json/{filename}.json', 'r') as f:
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