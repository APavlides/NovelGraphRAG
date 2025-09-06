from src.graph.node import Node


def initialise_graph():
    graph = StoryGraph()
    print("Graph initialized (empty, no seed data added).")
    return graph

class StoryGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node_type, name, content):
        node = Node(node_type, name, content)
        self.nodes.append(node)
        return node

    def find_nodes(self, node_type=None, name=None):
        return [
            n
            for n in self.nodes
            if (node_type is None or n.node_type == node_type)
            and (name is None or n.name == name)
        ]

    def get_relevant_context(self, chapter_outline):
        """
        Retrieve relevant context for chapter generation.
        For now, this returns a summary of all existing nodes.
        You can enhance this with more sophisticated retrieval logic.
        """
        if not self.nodes:
            return "No previous story content available."
        
        context_parts = []
        for node in self.nodes:
            # Create a brief summary of each node
            summary = f"- {node.node_type.title()}: {node.name}"
            if hasattr(node, 'content') and node.content:
                # Truncate content for brevity
                content_preview = str(node.content)[:200]
                if len(str(node.content)) > 200:
                    content_preview += "..."
                summary += f" - {content_preview}"
            context_parts.append(summary)
        
        return "\n".join(context_parts)
