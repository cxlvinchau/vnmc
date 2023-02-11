from typing import List, Any

from vnmc.graph.graph import Graph


def dfs(graph: Graph, nodes: List[Any]):
    stack = list(nodes)
    explored = set()
    while stack:
        current = stack.pop()
        explored.add(current)
        for succ in graph.get_graph_successors(current):
            if succ not in explored:
                explored.add(succ)


def tarjan(graph: Graph, node):
    necklace = []
    active = set()
    dfs_num = 0
    state_to_num = dict()
    sccs = []

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

    return sccs
