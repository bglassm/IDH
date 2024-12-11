import os

def rename_files(base_path='static/images'):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            old_path = os.path.join(root, file)
            new_path = os.path.join(root, file.replace(' ', '_').lower())
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")

rename_files()
