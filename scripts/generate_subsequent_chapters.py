from dotenv import load_dotenv

from src.ai.generator import ChapterGenerator
from src.graph.graph_manager import initialise_graph

load_dotenv()

if __name__ == "__main__":
    graph = initialise_graph()  # Or load from disk if you serialize your graph
    generator = ChapterGenerator(graph)
    # This should use RAG context, not seed data
    generator.generate_chapter("Maria investigates the old lighthouse")