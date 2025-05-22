import os
import re

def get_unique_filename(folder_path, fixed_id, fixed_name, fixed_form, ext):
    """
    Generate a unique filename by incrementing the number.
    """
    counter = 0
    while True:
        if fixed_form != " ":
            unique_filename = f"{fixed_id}_{counter}_{fixed_name.lower()}-{fixed_form.lower()}{ext}"
        else:
            unique_filename = f"{fixed_id}_{counter}_{fixed_name.lower()}{ext}"
        unique_file_path = os.path.join(folder_path, unique_filename)
        if not os.path.exists(unique_file_path):
            return unique_filename
        counter += 1

def rename_images_in_folder(folder_path):
    """
    Rename all image files in the specified folder with fixed ID, name, and form.
    """
    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    if not image_files:
        print("No PNG images found in the folder.")
        return

    print(f"Found {len(image_files)} images to rename.")

    for filename in image_files:
        print(f"\nCurrent file: {filename}")
        try:
            # Extract file extension
            _, ext = os.path.splitext(filename)

            # Generate a unique filename
            unique_filename = get_unique_filename(folder_path, FIXED_ID, FIXED_NAME, FIXED_FORM, ext)
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, unique_filename)

            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {filename} -> {unique_filename}")

        except Exception as e:
            print(f"Error processing file {filename}: {e}")

def replace_double_hyphen(folder_path):
    """
    Replace all instances of '--' with '-' in filenames within the specified folder.
    """
    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    files = os.listdir(folder_path)
    for filename in files:
        if "--" in filename:
            new_filename = filename.replace("--", "-")
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            try:
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

def replace_hyphen_with_space(folder_path):
    """
    Replace all instances of '-' with ' ' in filenames within the specified folder.
    """
    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    files = os.listdir(folder_path)
    for filename in files:
        if "-" in filename:
            new_filename = filename.replace("-", " ")
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            try:
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

def replace_last_underline_with_space(folder_path):
    """
    Replace the last instance of '_' with ' ' in filenames within the specified folder.
    """
    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    files = os.listdir(folder_path)
    for filename in files:
        if "_" in filename:
            parts = filename.rsplit("_", 1)
            new_filename = f"{parts[0]} {parts[1]}"
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            try:
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

def main():
    # Input the folder path
    folder_path = "./data/unused/rename folder"
    # image_folder = r"./data/image Dataset/dataset/dataset"

    # replace_double_hyphen(image_folder)
    # rename_images_in_folder(folder_path)
    # replace_hyphen_with_space(folder_path)
    replace_last_underline_with_space(folder_path)

# Define the fixed ID you want to use
FIXED_ID = "845"  # Change this number to your desired ID
FIXED_NAME = "Cramorant" # Change this to the desired Pokémon name
FIXED_FORM = " "  # Change this to the desired form (or leave empty for no form)
#FIXED_FORM = " "  # Change this to the desired form (or leave empty for no form)

if __name__ == "__main__":
    main()