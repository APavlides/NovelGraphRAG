from dotenv import load_dotenv

from src.ai.generator import ChapterGenerator
from src.graph.graph_manager import initialise_graph

load_dotenv()

if __name__ == "__main__":
    graph = initialise_graph()
    generator = ChapterGenerator(graph)
    generator.generate_chapter("David explores the crumbling cliffs")
    print("First chapter generated. Now run 'python scripts/index_novel_documents.py' to index it for RAG.")