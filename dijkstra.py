import heapq


def dijkstra_generator(graph, start_id: int, end_id: int):
    """
    Step-by-step Dijkstra generator. Yields one animation frame per step:
      {"type": "current", "node": u, "cost": c}          — node selected from heap (show blue)
      {"type": "visit",   "node": u, "cost": c}          — node settled (show yellow)
      {"type": "relax",   "node": v, "cost": c, "edge": (u,v)} — neighbour relaxed
      {"type": "done",    "path": [...], "total_cost": f, "reachable": bool}
    """
    nodes = graph.nodes
    INF = float("inf")

    dist = {nid: INF for nid in nodes}
    dist[start_id] = 0
    visited: set = set()
    parent: dict = {start_id: None}
    pq = [(0, start_id)]

    while pq:
        cost, u = heapq.heappop(pq)

        if u in visited:
            continue

        # Show node as "current" (blue) before settling
        yield {"type": "current", "node": u, "cost": cost}

        visited.add(u)

        # Settle the node (yellow)
        yield {"type": "visit", "node": u, "cost": cost, "visited": set(visited)}

        if u == end_id:
            break

        for v, w in graph.get_neighbors(u):
            if v in visited:
                continue
            new_cost = dist[u] + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                parent[v] = u
                heapq.heappush(pq, (new_cost, v))
                yield {"type": "relax", "node": v, "cost": new_cost, "edge": (u, v)}

    reachable = end_id in parent
    total_cost = dist.get(end_id, INF)
    path = reconstruct_path(parent, start_id, end_id) if reachable else []
    yield {"type": "done", "path": path, "total_cost": total_cost, "reachable": reachable}


def reconstruct_path(parent: dict, start_id: int, end_id: int) -> list:
    if end_id not in parent:
        return []
    path = []
    current = end_id
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path if path and path[0] == start_id else []
