class Node:
    def __init__(self, node_type, name, content):
        self.node_type = node_type
        self.name = name
        self.content = content
        self.edges = []

    def add_edge(self, node, relation):
        self.edges.append((node, relation))
