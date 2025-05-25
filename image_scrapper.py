import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Create directories if they don't exist
os.makedirs('./data/scrapped_images', exist_ok=True)
os.makedirs('./data/pokemon_images', exist_ok=True)

# Load Pokémon data for reference
pokemon_df = pd.read_csv('./data/Pokemon.csv')

def download_pokemon_sprites_from_csv():
    success_count = 0
    failure_count = 0
    skipped_count = 0

    for _, row in pokemon_df.iterrows():
        pokemon_id = str(row['ID'])
        name = row['Name']
        form = row['Form'] if not pd.isna(row['Form']) else " "
        form_suffix = f"-{form}" if form.strip() != "" and form.strip() != " " else ""
        filename = f"{pokemon_id}_{name}{form_suffix}.png"

        # Check if file already exists
        file_exists = False
        for dir_path in ['./data/scrapped_images', './data/pokemon_images']:
            filepath = os.path.join(dir_path, filename)
            if os.path.isfile(filepath):
                file_exists = True
                break

        if file_exists:
            print(f"Skipping existing image: {filename}")
            skipped_count += 1
            continue

        # Build the detail page URL
        detail_url = f"https://pokemondb.net/pokedex/{name.lower().replace(' ', '-')}"
        print(f"Fetching detail page: {detail_url}")

        try:
            detail_response = requests.get(detail_url)
            if detail_response.status_code != 200:
                print(f"Failed to access detail page for {name}: Status {detail_response.status_code}")
                failure_count += 1
                continue

            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Try to find the correct image for the form
            img_url = None
            if form.strip() == "" or form.strip() == " ":
                # Try to get the main sprite
                img = detail_soup.select_one('img.sprite-main')
                if img:
                    img_url = img.get('src')
            else:
                # Try to find an image with the form name in the alt text
                img = detail_soup.find('img', alt=lambda x: x and form.lower() in x.lower())
                if img:
                    img_url = img.get('src')

            if not img_url:
                print(f"Could not find image for {name} {form}")
                failure_count += 1
                continue

            print(f"Downloading {filename} from {img_url}")
            img_response = requests.get(img_url, timeout=10)
            if img_response.status_code != 200:
                print(f"Failed to download image for {name} {form}: Status {img_response.status_code}")
                failure_count += 1
                continue

            # Save to both directories
            for dir_path in ['./data/scrapped_images', './data/pokemon_images']:
                filepath = os.path.join(dir_path, filename)
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

            success_count += 1
            print(f"Successfully saved: {filename}")

        except Exception as e:
            print(f"Error downloading {name} {form}: {str(e)}")
            failure_count += 1

        time.sleep(0.5)

    print(f"\nScraping completed: {success_count} sprites downloaded, {failure_count} failed, {skipped_count} skipped (already existed)")

def compare_images_and_csv():
    """
    Compare the images in the directories with the CSV data.
    This function checks if all Pokémon in the CSV have corresponding images.
    """
    # make both lower case
    image_files = set(os.listdir('./data/scrapped_images')) | set(os.listdir('./data/pokemon_images'))
    image_files = {img.lower() for img in image_files if img.endswith('.png')}
    csv_pokemon = set(pokemon_df['Name'].str.lower())

    missing_images = []
    for name in csv_pokemon:
        if not any(f"{name}.png" in img for img in image_files):
            missing_images.append(name)

    if missing_images:
        print(f"Missing images for Pokémon: {', '.join(missing_images)}")
    else:
        print("All Pokémon in the CSV have corresponding images.")

if __name__ == "__main__":
    # download_pokemon_sprites_from_csv()
    compare_images_and_csv()