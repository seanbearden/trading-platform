import os


def delete_files(file_paths: list):
    # Check if the file exists and delete it
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
