class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn
    
    def reachable_nodes(self):
        visited = set()
        queue = [self.start]
        visited.add(self.start)
        self.visit_fn(self.start)
        result = [self.start]
        
        while queue:
            node = queue.pop(0)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    self.visit_fn(neighbor)
                    queue.append(neighbor)
                    result.append(neighbor)
        
        return result