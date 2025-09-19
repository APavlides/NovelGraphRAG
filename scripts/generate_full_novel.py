#!/usr/bin/env python3
"""
Iterative Novel Generation Script

Generate    with open(structure_path, 'r', encoding='utf-8') as f:
        structure_config = yaml.safe_load(f)
    
    # Read overview for story details
    overview_path = seed_dir / \"overview.md\"
    overview_content = \"\"
    if overview_path.exists():
        with open(overview_path, 'r', encoding='utf-8') as f:lete novel by:
1. Generating first chapter from seed data
2. Indexing generated content for RAG
3. Iteratively generating subsequent chapters using RAG context
4. Analyzing each chapter for quality
5. Continuing until novel is complete

Usage:
    python scripts/generate_full_novel.py [--max-chapters N] [--analyze-each] [--pause-between]
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add the project root to sys.path so 'src' is importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import argparse
import os

import yaml

print("\n".join(sys.path))



from src.ai.generator import ChapterGenerator
from src.graph.graph_manager import StoryGraph


def run_script(script_name: str, description: str) -> bool:
    """Run a script and return success status."""
    print(f"\n{'='*60}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    result = os.system(f"python -m {script_name}")
    
    if result == 0:
        print(f"✅ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed with exit code {result}")
        return False


def run_analysis_script() -> bool:
    """Run the chapter analysis script."""
    print("\n" + "="*60)
    print("📊 Analyzing Generated Chapter Quality")
    print("="*60)
    
    result = os.system("python scripts/analyze_chapter.py")
    
    if result == 0:
        print("✅ Chapter analysis completed")
        return True
    else:
        print(f"❌ Chapter analysis failed with exit code {result}")
        return False


def get_novel_config():
    """Read novel configuration from seed data files."""
    seed_dir = Path("data/seed")
    
    # Read structure configuration
    structure_path = seed_dir / "structure.yaml"
    if not structure_path.exists():
        raise FileNotFoundError(f"Structure configuration not found: {structure_path}")
    
    with open(structure_path, 'r', encoding='utf-8') as f:
        structure_config = yaml.safe_load(f)
    
    # Read scenes/chapters configuration
    scenes_path = seed_dir / "scenes.yaml"
    scenes_config = {}
    if scenes_path.exists():
        with open(scenes_path, 'r', encoding='utf-8') as f:
            scenes_config = yaml.safe_load(f)
    
    # Read overview for story details
    overview_path = seed_dir / "overview.md"
    overview_content = ""
    if overview_path.exists():
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview_content = f.read()
    
    # Get chapter count from scenes.yaml if available, otherwise default
    chapter_count = 12  # fallback
    if scenes_config and 'novel_structure' in scenes_config:
        chapter_count = scenes_config['novel_structure'].get('total_chapters', 12)
    
    return {
        'structure': structure_config,
        'scenes': scenes_config,
        'overview': overview_content,
        'title': extract_title_from_overview(overview_content),
        'genre': structure_config.get('genre', {}),
        'validation': structure_config.get('validation', {}),
        'chapter_count': chapter_count
    }


def extract_title_from_overview(overview_content: str) -> str:
    """Extract the novel title from overview markdown."""
    lines = overview_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Novel"


def check_novel_directory():
    """Ensure the novel directory exists and is ready."""
    novel_dir = Path("data/novel")
    if not novel_dir.exists():
        novel_dir.mkdir(parents=True)
        print(f"📁 Created novel directory: {novel_dir}")


def get_existing_chapters():
    """Get list of existing chapter files."""
    novel_dir = Path("data/novel")
    if not novel_dir.exists():
        return []
    
    chapter_files = list(novel_dir.glob("chapter_*.md"))
    return sorted(chapter_files)


def generate_novel(max_chapters: int = 12, analyze_each: bool = True, pause_between: bool = False):
    """Generate the complete novel iteratively."""
    
    # Read configuration from seed data
    try:
        config = get_novel_config()
        novel_title = config['title']
        genre_info = config['genre']
        
        # Use chapter count from scenes.yaml if max_chapters wasn't specified
        if max_chapters == 12:  # Default value
            max_chapters = config['chapter_count']
            
    except (FileNotFoundError, yaml.YAMLError, KeyError, ImportError) as e:
        print(f"❌ Error reading novel configuration: {e}")
        print("💡 Make sure your data/seed/ directory contains structure.yaml and overview.md")
        return
    
    print("🎭 NovelGraphRAG: Iterative Novel Generation")
    print("=" * 60)
    print(f"📚 Generating '{novel_title}'")
    if genre_info:
        genre_type = genre_info.get('type', 'fiction')
        subgenre = genre_info.get('subgenre', '')
        if subgenre:
            print(f"📖 Genre: {genre_type} ({subgenre})")
        else:
            print(f"📖 Genre: {genre_type}")
    print(f"🎯 Target: {max_chapters} chapters")
    if analyze_each:
        print("📊 Will analyze each chapter for quality")
    if pause_between:
        print("⏸️  Will pause between chapters for review")
    print()
    
    # Initialize
    check_novel_directory()
    graph = StoryGraph()
    generator = ChapterGenerator(graph)
    
    # Check for existing chapters
    existing_chapters = get_existing_chapters()
    if existing_chapters:
        print(f"📄 Found {len(existing_chapters)} existing chapters:")
        for chapter in existing_chapters:
            print(f"   • {chapter.name}")
        
        response = input("\n🤔 Continue from where we left off? (y/n): ").lower().strip()
        if response != 'y':
            print("🛑 Aborting to avoid overwriting existing work")
            return
        
        start_chapter = len(existing_chapters)
        print(f"▶️  Starting from chapter {start_chapter + 1}")
    else:
        start_chapter = 0
        print("🆕 Starting fresh novel generation")
    
    # Generate chapters
    successful_chapters = start_chapter
    
    for chapter_num in range(start_chapter, max_chapters):
        print(f"\n🔄 CHAPTER {chapter_num + 1} of {max_chapters}")
        print("-" * 60)
        
        try:
            if chapter_num == 0 and start_chapter == 0:
                # Generate first chapter from seed data
                success = run_script("scripts.generate_first_chapter", 
                                   "Generating Chapter 1 from seed data")
            else:
                # Generate subsequent chapter using RAG
                print(f"🤖 Generating Chapter {chapter_num + 1} using RAG context...")
                
                # Use the generator directly for subsequent chapters
                try:
                    # Let the generator decide what to write based on existing context
                    generator.generate_chapter(
                        chapter_outline=f"Continue the story - Chapter {chapter_num + 1}"
                    )
                    print(f"✅ Chapter {chapter_num + 1} generated successfully")
                    success = True
                except (FileNotFoundError, RuntimeError) as e:
                    print(f"❌ Chapter {chapter_num + 1} generation failed: {e}")
                    success = False
            
            if not success:
                print(f"💥 Failed to generate Chapter {chapter_num + 1}")
                break
            
            successful_chapters += 1
            
            # Index the newly generated content for RAG
            if chapter_num < max_chapters - 1:  # Don't index the last chapter
                index_success = run_script("scripts.index_novel_documents", 
                                          f"Indexing Chapter {chapter_num + 1} for RAG")
                if not index_success:
                    print(f"⚠️  Indexing failed for Chapter {chapter_num + 1}, but continuing...")
            
            # Analyze chapter quality if requested
            if analyze_each:
                run_analysis_script()
            
            # Pause between chapters if requested
            if pause_between and chapter_num < max_chapters - 1:
                print(f"\n⏸️  Chapter {chapter_num + 1} complete.")
                input("Press Enter to continue to next chapter...")
            
            print(f"✨ Chapter {chapter_num + 1} completed successfully!")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Generation interrupted by user after {successful_chapters} chapters")
            break
        except (FileNotFoundError, yaml.YAMLError, RuntimeError) as e:
            print(f"💥 Unexpected error generating Chapter {chapter_num + 1}: {e}")
            break
    
    # Final summary
    print("\n🎉 NOVEL GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📚 Successfully generated: {successful_chapters} chapters")
    print("📁 Location: data/novel/")
    
    if successful_chapters > 0:
        print("\n📖 Your novel chapters:")
        final_chapters = get_existing_chapters()
        for i, chapter in enumerate(final_chapters, 1):
            print(f"   {i:2d}. {chapter.name}")
        
        print(f"\n✨ Your novel '{novel_title}' is ready!")
        print("🔍 Run 'python scripts/analyze_chapter.py' to analyze any chapter")
        print("🧹 Run 'python scripts/refresh_all.py' to clean up and start over")
    else:
        print("\n😞 No chapters were successfully generated.")
        print("🔧 Check your configuration and try again.")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a complete novel iteratively using NovelGraphRAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_full_novel.py                    # Generate full novel with defaults
  python scripts/generate_full_novel.py --max-chapters 5  # Generate only 5 chapters  
  python scripts/generate_full_novel.py --no-analyze      # Skip quality analysis
  python scripts/generate_full_novel.py --pause-between   # Pause between chapters
        """
    )
    
    parser.add_argument(
        "--max-chapters", 
        type=int, 
        default=None, 
        help="Maximum number of chapters to generate (default: from genre configuration)"
    )
    
    parser.add_argument(
        "--analyze-each", 
        action="store_true", 
        default=True,
        help="Analyze each chapter after generation (default: True)"
    )
    
    parser.add_argument(
        "--no-analyze", 
        action="store_false", 
        dest="analyze_each",
        help="Skip chapter analysis"
    )
    
    parser.add_argument(
        "--pause-between", 
        action="store_true", 
        default=False,
        help="Pause between chapters for manual review"
    )
    
    args = parser.parse_args()
    
    try:
        # If no max_chapters specified, let the function determine from config
        max_chapters = args.max_chapters if args.max_chapters is not None else 12
        
        generate_novel(
            max_chapters=max_chapters,
            analyze_each=args.analyze_each, 
            pause_between=args.pause_between
        )
    except KeyboardInterrupt:
        print("\n👋 Novel generation interrupted. Partial progress saved.")
    except (FileNotFoundError, yaml.YAMLError, ImportError) as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()