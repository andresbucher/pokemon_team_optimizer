import os

def get_image_path(pokemon_id, name, form):
    """Get image path for a Pokemon"""
    base_folder = r"./data/pokemon_images"
    # Clean up form for filename
    form = form.strip()
    if form and form != " ":
        filename = f"{pokemon_id}_{name}-{form}.png"
    else:
        filename = f"{pokemon_id}_{name}.png"
    filepath = os.path.join(base_folder, filename)
    if os.path.isfile(filepath):
        return filepath
    # If no image is found, return a placeholder image
    return "./data/misc_images/substitute.png"