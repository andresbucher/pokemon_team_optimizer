import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re

# Create directories if they don't exist
os.makedirs('./data/scrapped_images', exist_ok=True)
os.makedirs('./data/pokemon_images', exist_ok=True)

# Load Pokémon data for reference
pokemon_df = pd.read_csv('./data/Pokemon.csv')

def download_pokemon_sprites():
    # Main sprites page URL
    main_url = "https://pokemondb.net/sprites"
    
    print("Fetching main sprites page...")
    response = requests.get(main_url)
    
    if response.status_code != 200:
        print(f"Failed to access main sprites page: Status {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all Pokémon entries - updated selector based on the actual HTML structure
    pokemon_cards = soup.select('a.infocard')
    
    print(f"Found {len(pokemon_cards)} Pokémon cards on the main page")
    
    success_count = 0
    failure_count = 0
    skipped_count = 0
    
    # Create dictionaries for quick lookups
    pokemon_name_to_id = {}
    pokemon_id_form_dict = {}
    
    for _, row in pokemon_df.iterrows():
        pokemon_id = str(row['ID'])
        name = row['Name']
        form = row['Form'] if not pd.isna(row['Form']) else " "
        
        # Create a mapping from name to ID
        pokemon_name_to_id[name.lower()] = pokemon_id
        
        # Create a mapping from ID+name+form to form value
        key = f"{pokemon_id}_{name}_{form}"
        pokemon_id_form_dict[key] = form
    
    # Process each Pokémon card
    for card in pokemon_cards:
        try:
            # Extract the Pokémon name from the text content
            name = card.get_text().strip()
            
            # Extract the href attribute for the detail URL
            href = card.get('href', '')
            detail_url = 'https://pokemondb.net' + href if href else None
            
            if not detail_url:
                print(f"No detail URL found for {name}, skipping...")
                failure_count += 1
                continue
            
            # Extract the image URL for the base form
            img = card.select_one('img.icon-pkmn')
            if not img:
                print(f"No image found for {name}, skipping...")
                failure_count += 1
                continue
                
            img_url = img.get('src', '')
            
            # Look up the Pokémon ID from our mapping
            pokemon_id = pokemon_name_to_id.get(name.lower())
            
            # If we couldn't find it in our mapping, try to extract from the URL
            if not pokemon_id:
                # Try to extract ID from the URL or href
                id_match = re.search(r'/(\d+)-', img_url)
                if not id_match:
                    id_match = re.search(r'/(\d+)\.', img_url)
                
                if id_match:
                    pokemon_id = id_match.group(1)
                else:
                    print(f"Could not determine ID for {name}, skipping...")
                    failure_count += 1
                    continue
            
            print(f"Processing Pokémon: #{pokemon_id} {name}")
            
            # Get all forms for this Pokémon by visiting the detail page
            print(f"Fetching detail page: {detail_url}")
            detail_response = requests.get(detail_url)
            if detail_response.status_code != 200:
                print(f"Failed to access detail page for {name}: Status {detail_response.status_code}")
                failure_count += 1
                continue
            
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            
            # Create a set to hold all form variants we'll need to download
            forms_to_download = set()
            
            # First, add the base form
            forms_to_download.add(" ")
            
            # Look for form headers and tabs to find all variants
            form_headers = detail_soup.select('h3')
            for header in form_headers:
                header_text = header.get_text().strip()
                
                # Check if header mentions forms
                if any(keyword in header_text.lower() for keyword in ['form', 'mega', 'regional', 'variant', 'alolan', 'galarian']):
                    # The next elements might contain form names
                    next_elements = header.find_next_siblings()
                    for elem in next_elements[:10]:  # Check next 10 elements
                        if elem.name == 'h3' or elem.name == 'h2':
                            break  # Stop if we hit another header
                        
                        # Look for form names in text
                        text = elem.get_text().strip()
                        if any(form_name in text.lower() for form_name in ['mega', 'alolan', 'galarian', 'hisuian', 'paldean']):
                            # Extract the specific form name
                            form_matches = re.findall(r'(Mega[-\s]?[XYZ]?|Alolan|Galarian|Hisuian|Paldean|Gigantamax|G-Max)', text, re.IGNORECASE)
                            for form_match in form_matches:
                                forms_to_download.add(form_match.strip())
            
            # Look for tabs that might indicate forms
            form_tabs = detail_soup.select('.tabset-basics .tabs-tab')
            for tab in form_tabs:
                tab_text = tab.get_text().strip()
                if tab_text.lower() not in ['standard', 'normal', 'base'] and len(tab_text) > 0:
                    forms_to_download.add(tab_text.strip())
            
            # Check our CSV data for this Pokémon's forms
            for key, form_value in pokemon_id_form_dict.items():
                if key.startswith(f"{pokemon_id}_{name}_") and form_value != " ":
                    forms_to_download.add(form_value)
            
            # Now process each form
            for form in forms_to_download:
                try:
                    # Get the appropriate form URL
                    if form == " ":
                        # Base form - use the original image URL
                        current_form_url = img_url
                        form_display = "Base form"
                    else:
                        # Try to find form-specific image
                        form_display = form
                        # We'll attempt to modify the URL for the specific form
                        form_slug = form.lower().replace(' ', '-')
                        current_form_url = img_url.replace('.png', f'-{form_slug}.png')
                    
                    # Create the filename
                    form_suffix = f"-{form}" if form and form != " " else ""
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
                    
                    # Prefer high-quality sprites over icons
                    better_form_url = current_form_url.replace('/icon/', '/normal/')
                    
                    print(f"Downloading {form_display}: {better_form_url} as {filename}")
                    img_response = requests.get(better_form_url, timeout=10)
                    
                    if img_response.status_code != 200:
                        # Fallback to original URL if better image not available
                        print(f"Using fallback URL for {name} {form_display}")
                        img_response = requests.get(current_form_url, timeout=10)
                        
                    if img_response.status_code != 200:
                        # Try one more fallback - look for it in the HTML
                        if form != " ":
                            # Look for images that might contain the form name
                            form_images = detail_soup.select('img[alt*="' + form + '"]')
                            if form_images:
                                form_src = form_images[0].get('src', '')
                                if form_src:
                                    print(f"Found alternative image source for {name} {form}")
                                    img_response = requests.get(form_src, timeout=10)
                        
                    if img_response.status_code != 200:
                        print(f"Failed to download sprite for {name} {form_display}: Status {img_response.status_code}")
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
            
            # Add a delay to be nice to the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing card: {str(e)}")
            failure_count += 1
    
    print(f"\nScraping completed: {success_count} sprites downloaded, {failure_count} failed, {skipped_count} skipped (already existed)")

# Updated image path function for the optimizer
def get_image_path(pokemon_id, name, form):
    base_folder = r"./data/pokemon_images"
    
    # Format the filename exactly as we expect it
    form_suffix = f"-{form}" if form and form.strip() != " " else ""
    filename = f"{pokemon_id}_{name}{form_suffix}.png"
    
    # Check if the file exists
    filepath = os.path.join(base_folder, filename)
    if os.path.isfile(filepath):
        return filepath
    
    # If not found, return placeholder
    return "./data/misc_images/substitute.png"

if __name__ == "__main__":
    download_pokemon_sprites()