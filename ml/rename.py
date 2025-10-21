import os

def rename_images(folder_path, base_name, extension=".jpg"):
    # Get all files in the folder with the given extension
    exts = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
    files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in exts]

    # Sort files alphabetically (optional, keeps consistent ordering)
    files.sort()

    # Loop through and rename each file
    for idx, file_name in enumerate(files, start=1):
        old_path = os.path.join(folder_path, file_name)
        new_name = f"{base_name} {idx}{extension}"
        new_path = os.path.join(folder_path, new_name)
        
        os.rename(old_path, new_path)


# Example usage
if __name__ == "__main__":
    folder_path = ""
    base_name = ""
    rename_images(folder_path, base_name)
