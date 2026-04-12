import sys
from pathlib import Path


def _resource_base_path():
    """Return the root folder that contains the data directory."""
    # PyInstaller extracts bundled files to _MEIPASS at runtime.
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def _data_path(*parts):
    return _resource_base_path() / 'data' / Path(*parts)

def get_image_path(pokemon_id, name, form):
    """Get image path for a Pokemon"""
    base_folder = _data_path('pokemon_images')
    # Clean up form for filename
    form = form.strip()
    if form and form != " ":
        filename = f"{pokemon_id}_{name}-{form}.png"
    else:
        filename = f"{pokemon_id}_{name}.png"
    filepath = base_folder / filename
    if filepath.is_file():
        return str(filepath)
    # If no image is found, return a placeholder image
    return str(_data_path('misc_images', 'substitute.png'))