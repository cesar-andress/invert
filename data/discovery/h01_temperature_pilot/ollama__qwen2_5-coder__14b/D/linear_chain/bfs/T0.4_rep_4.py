from collections import deque

class GraphTraversal:
    def __init__(self, graph, start, visit_fn):
        self.graph = graph
        self.start = start
        self.visit_fn = visit_fn

    def reachable_nodes(self):
        visited = set()
        queue = deque([self.start])
        
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                self.visit_fn(node)
                queue.extend(self.graph.get(node, []))
        
        return sorted(visited)