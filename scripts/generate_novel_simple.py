#!/usr/bin/env python3
"""
Simple Novel Generation Script

A streamlined script that generates a complete novel by iterating through chapters.
Each chapter is generated, indexed, and then the next chapter uses that context.
Reads configuration from your seed data files.

Usage:
    python scripts/generate_novel_simple.py
"""

import os
import sys
from pathlib import Path

import yaml


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n📝 {description}...")
    result = os.system(command)
    
    if result == 0:
        print(f"✅ {description} completed")
        return True
    else:
        print(f"❌ {description} failed")
        return False

def get_novel_info():
    """Read basic novel information from seed data."""
    seed_dir = Path("data/seed")
    
    # Read title from overview.md
    overview_path = seed_dir / "overview.md"
    title = "Your Novel"
    
    if overview_path.exists():
        with open(overview_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
    
    # Read scenes/chapters configuration for accurate chapter count
    scenes_path = seed_dir / "scenes.yaml"
    if scenes_path.exists():
        try:
            with open(scenes_path, 'r', encoding='utf-8') as f:
                scenes_config = yaml.safe_load(f)
                if scenes_config and 'novel_structure' in scenes_config:
                    chapter_count = scenes_config['novel_structure'].get('total_chapters', 12)
        except Exception:  # pylint: disable=broad-except
            # If we can't read the scenes file, fall back to structure.yaml
            pass
    
    # Fallback: Read genre info from structure.yaml if available
    structure_path = seed_dir / "structure.yaml"
    chapter_count = 12  # Default
    
    if structure_path.exists():
        try:
            with open(structure_path, 'r', encoding='utf-8') as f:
                structure_config = yaml.safe_load(f)
                genre_type = structure_config.get('genre', {}).get('type', 'literary_fiction')
                
                # Default chapter counts based on genre
                defaults = {
                    'literary_fiction': 12,
                    'commercial_fiction': 20,
                    'mystery': 15,
                    'romance': 18,
                    'fantasy': 25,
                    'sci_fi': 20
                }
                chapter_count = defaults.get(genre_type, 12)
        except Exception:  # pylint: disable=broad-except
            # If we can't read the structure file, use defaults
            pass
    
    return title, chapter_count


def main():
    """Generate the complete novel."""
    
    # Get novel information from seed data
    title, chapter_count = get_novel_info()
    
    print(f"🎭 Generating '{title}' - Complete Novel")
    print("=" * 60)
    print(f"📚 {chapter_count} chapters planned")
    print()
    
    # Step 1: Generate first chapter from seed data
    if not run_command("python -m scripts.generate_first_chapter", 
                      "Generating Chapter 1 from seed data"):
        return
    
    # Step 2: Index first chapter
    if not run_command("python scripts/index_novel_documents.py", 
                      "Indexing Chapter 1 for RAG context"):
        return
    
    # Step 3: Generate remaining chapters iteratively
    for i in range(2, chapter_count + 1):
        print(f"\n{'='*60}")
        print(f"📖 CHAPTER {i}")
        print(f"{'='*60}")
        
        # Generate chapter using RAG context
        if not run_command("python -m scripts.generate_subsequent_chapters", 
                          f"Generating Chapter {i}"):
            print(f"💥 Failed to generate Chapter {i}. Stopping.")
            break
        
        # Index the new chapter (except for the last one)
        if i < chapter_count:
            if not run_command("python scripts/index_novel_documents.py", 
                              f"Indexing Chapter {i} for RAG"):
                print(f"⚠️  Failed to index Chapter {i}, but continuing...")
        
        print(f"✅ Chapter {i} completed!")
    
    # Final summary
    print("\n🎉 NOVEL GENERATION COMPLETE!")
    print("=" * 50)
    
    # List generated chapters
    novel_dir = Path("data/novel")
    if novel_dir.exists():
        chapters_found = sorted(novel_dir.glob("*.md"))
        print(f"📚 Generated {len(chapters_found)} chapter files:")
        for chapter in chapters_found:
            print(f"   • {chapter.name}")
    
    print(f"\n✨ Your novel '{title}' is ready!")
    print("📊 Run 'python scripts/analyze_chapter.py' to analyze quality")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Generation interrupted. Partial progress saved in data/novel/")
    except Exception as e:  # pylint: disable=broad-except
        print(f"\n💥 Error: {e}")
        sys.exit(1)