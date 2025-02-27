import os

def list_files(directory):
    """Returns a list of files in a directory."""
    print("X")
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

