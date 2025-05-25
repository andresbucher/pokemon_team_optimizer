def verify_image_database(image_folder):
    import os
    import re
    from collections import defaultdict

    pokemon_groups = defaultdict(set)  # Use a set to avoid duplicates
    pattern = r"(\d+)_([a-zA-Z0-9]+)(?:-(.*))?.png"  # Matches ID, Name, and optional Form

    all_files = os.listdir(image_folder)

    print("\nMatching filenames against the pattern:")
    for file_name in all_files:
        match = re.match(pattern, file_name)
        if match:
            # Extract components
            pokemon_id, name, form = match.groups()
            form = form if form else "Base"  # Default to "Base" if no form
            key = (pokemon_id, name.lower())  # Use lowercase to avoid case mismatch issues
            pokemon_groups[key].add(form)  # Add form to the set
            print(f"Matched: ID={pokemon_id}, Name={name}, Form={form}")
        else:
            print(f"Skipping file: {file_name} (Does not match the pattern)")

    # Aggregate Pokémon by Name and check for split IDs
    name_to_ids = defaultdict(set)
    for (pokemon_id, name), forms in pokemon_groups.items():
        name_to_ids[name].add(pokemon_id)

    print("\nIdentifying potential ID conflicts:")
    for name, ids in name_to_ids.items():
        if len(ids) > 1:  # If a Pokémon has multiple IDs
            print(f"Conflicting Name: {name} spans multiple IDs: {ids}")

    # Print Pokémon with multiple forms under the same ID
    print("\nPokémon with multiple forms:")
    for (pokemon_id, name), forms in pokemon_groups.items():
        if len(forms) > 1:
            print(f"ID={pokemon_id}, Name={name} has multiple forms: {list(forms)}")

# Example Usage
image_folder = r"./data/image Dataset/dataset/dataset" # Replace with your folder path
verify_image_database(image_folder)



image_folder = r"./data/image Dataset/dataset/dataset"
image_folder = r"./data/image Dataset/dataset/dataset"