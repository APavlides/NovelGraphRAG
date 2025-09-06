import os

import yaml

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed"))

def load_seed_data():
    # Load overview
    overview_path = os.path.join(DATA_DIR, "overview.md")
    with open(overview_path, "r") as f:
        overview = f.read().strip()

    # Load characters
    characters_path = os.path.join(DATA_DIR, "characters.yaml")
    with open(characters_path, "r") as f:
        characters = yaml.safe_load(f)

    # Load arcs
    arcs_path = os.path.join(DATA_DIR, "arcs.yaml")
    with open(arcs_path, "r") as f:
        arcs = yaml.safe_load(f)

    # Optionally load world info
    world_path = os.path.join(DATA_DIR, "world.yaml")
    world = None
    if os.path.exists(world_path):
        with open(world_path, "r") as f:
            world = yaml.safe_load(f)

    return {
        "overview": overview,
        "characters": characters,
        "arcs": arcs,
        "world": world,
    }