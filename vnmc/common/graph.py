import abc


class Graph(abc.ABC):

    @abc.abstractmethod
    def get_graph_successors(self, node):
        pass

    def get_graph_predecessors(self, node):
        return set()


class GraphNode(abc.ABC):

    def __init__(self, name, node_id, **kwargs):
        self.name = name
        self.node_id = node_id
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, GraphNode):
            return other.name == self.name and other.node_id == self.node_id
        return False

    def __hash__(self):
        return self.node_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class GraphEdge(abc.ABC):

    def __init__(self, source: GraphNode, target: GraphNode, **kwargs):
        self.source = source
        self.target = target
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, GraphEdge):
            return other.source == self.source and other.target == self.target and other.kwargs == self.kwargs
        return False

    def __hash__(self):
        return hash(self.source) + hash(self.target)

    def __str__(self):
        return f"{str(self.source)} -> {str(self.target)}"
