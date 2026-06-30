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
                queue.extend(neighbor for neighbor in self.graph[node] if neighbor not in visited)
        
        return sorted(visited)  # or return visited as a set