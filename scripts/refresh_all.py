#!/usr/bin/env python3

import glob
import os
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Delete all generated chapter files (e.g., chapter_*.md)
chapter_files = glob.glob(os.path.join(PROJECT_ROOT, "chapter_*.md"))
for file in chapter_files:
    try:
        os.remove(file)
        print(f"Deleted {file}")
    except Exception as e:
        print(f"Could not delete {file}: {e}")

# Delete index/graph data directories (e.g., data_index, graph_data, etc.)
for folder in ["data_index", "graph_data"]:
    folder_path = os.path.join(PROJECT_ROOT, folder)
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Deleted {folder_path}")
        except (FileNotFoundError, PermissionError) as e:
            print(f"Could not delete {folder_path}: {e}")
