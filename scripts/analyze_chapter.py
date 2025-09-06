#!/usr/bin/env python3
"""
Analyze generated chapter against structure configuration requirements.
"""

from pathlib import Path

import yaml


def load_structure_config():
    """Load the structure configuration."""
    config_path = Path("data/seed/structure.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def analyze_chapter(chapter_path, config):
    """Analyze a chapter against configuration requirements."""
    with open(chapter_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    print(f"📖 Analyzing: {chapter_path}")
    print("=" * 60)
    
    # Check required elements
    first_chapter_config = config.get('chapter_requirements', {}).get('first_chapter', {})
    required_elements = first_chapter_config.get('required_elements', [])
    
    print("\n🔍 Required Elements Check:")
    for element in required_elements:
        found = element.lower() in content
        status = "✅" if found else "❌"
        print(f"  {status} '{element}': {'Found' if found else 'Missing'}")
    
    # Check character requirements
    char_requirements = first_chapter_config.get('character_requirements', {})
    print(f"\n👥 Character Requirements:")
    for role, requirement in char_requirements.items():
        print(f"  📝 {role.replace('_', ' ').title()}: {requirement}")
    
    # Basic content stats
    print(f"\n📊 Content Stats:")
    print(f"  📄 Length: {len(content)} characters")
    print(f"  📝 Words: ~{len(content.split())} words")
    
    # Check for key character names (from our seed data)
    key_characters = ['david', 'maria', 'ghost']
    print(f"\n🎭 Key Characters Mentioned:")
    for char in key_characters:
        found = char in content
        status = "✅" if found else "❌"
        print(f"  {status} {char.title()}: {'Present' if found else 'Missing'}")

if __name__ == "__main__":
    config = load_structure_config()
    chapter_path = Path("data/novel/chapter_david_explores_the_crumbling_cliffs.md")
    
    if chapter_path.exists():
        analyze_chapter(chapter_path, config)
    else:
        print(f"❌ Chapter not found: {chapter_path}")
