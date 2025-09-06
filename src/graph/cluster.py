class Cluster:
    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = nodes if nodes else []

    def add_node(self, node):
        self.nodes.append(node)
