import os

def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.abspath(path)

def check_existing_file(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)