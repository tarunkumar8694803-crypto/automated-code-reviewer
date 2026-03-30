import os

def get_all_python_files(directory="."):
    """Finds all .py files in the project, skipping hidden and venv folders."""
    python_files = []
    # Folders to ignore so we don't scan thousands of library files
    ignore_folders = {'venv', '.git', '__pycache__', '.pytest_cache'}

    for root, dirs, files in os.walk(directory):
        # Remove ignored folders from the search list
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            if file.endswith(".py"):
                # Use absolute paths to avoid any confusion
                python_files.append(os.path.abspath(os.path.join(root, file)))
    return python_files