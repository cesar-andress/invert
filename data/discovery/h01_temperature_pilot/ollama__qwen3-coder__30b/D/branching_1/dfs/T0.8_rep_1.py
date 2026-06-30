class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
        self.visited = set()
    
    def reachable_nodes(self):
        result = []
        stack = [self.start]
        
        while stack:
            node = stack.pop()
            if node not in self.visited:
                self.visited.add(node)
                self.visit_fn(node)
                result.append(node)
                # Add neighbors in reverse order to maintain original adjacency list order
                for neighbor in reversed(self.graph[node]):
                    if neighbor not in self.visited:
                        stack.append(neighbor)
        
        return result