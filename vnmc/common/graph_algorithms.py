from collections import deque
from typing import List, Any, Callable

from vnmc.common.graph import Graph


def dfs(graph: Graph, nodes: List[Any]):
    stack = list(nodes)
    explored = set()
    while stack:
        current = stack.pop()
        explored.add(current)
        for succ in graph.get_graph_successors(current):
            if succ not in explored:
                explored.add(succ)


def get_path(graph: Graph, node, targets):
    pred = dict()
    queue = deque([node])
    explored = set()
    targets = set(targets)
    target = None
    while queue:
        current = queue.popleft()
        if current in targets:
            target = current
            break
        explored.add(current)
        for succ in graph.get_graph_successors(current):
            if succ not in explored:
                pred[succ] = node
                queue.append(succ)

    # Backtrack
    if target is None:
        raise ValueError("Cannot find path to targets")

    path = deque()
    current = target
    while current != node:
        path.appendleft(current)
        current = pred[current]
    path.appendleft(current)

    return path


def tarjan(graph: Graph, node):
    necklace = []
    active = set()
    dfs_num = 0
    state_to_num = dict()
    sccs = []
    pred = dict()

    def tarjan_dfs(node):
        nonlocal dfs_num
        state_to_num[node] = dfs_num
        dfs_num += 1
        active.add(node)
        necklace.append((node, {node}))

        for succ in graph.get_graph_successors(node):
            if succ in active:
                scc = set()
                u, subset = necklace.pop()
                scc = scc.union(subset)
                while state_to_num[u] > state_to_num[succ]:
                    u, subset = necklace.pop()
                    scc = scc.union(subset)
                necklace.append((u, scc))
            elif succ not in state_to_num:
                pred[succ] = node
                tarjan_dfs(succ)

        root, scc = necklace[-1]
        if root == node:
            necklace.pop()
            sccs.append(scc)
            for node in scc:
                active.remove(node)

    tarjan_dfs(node)

    # Only return real SCCs
    sccs = [scc for scc in sccs if len(scc) > 1 or next(iter(scc)) in graph.get_graph_successors(next(iter(scc)))]

    return sccs, pred


def graph_to_dot(graph: Graph, node: Any, node_formatter: Callable[[Any], str] = None):
    nodes, edges = set(), []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        nodes.add(current)
        for succ in graph.get_graph_successors(current):
            if succ not in nodes and succ not in queue:
                queue.append(succ)
            edges.append((current, succ))

    out = "digraph G{\n"
    for node in nodes:
        out += f"{str(node)} [label=\"{str(node) if node_formatter is None else node_formatter(node)}\"]\n"
    for source, target in edges:
        out += f"{str(source)} -> {str(target)}\n"
    return out + "}"