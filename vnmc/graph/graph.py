import abc


class Graph(abc.ABC):

    @abc.abstractmethod
    def get_graph_successors(self, node):
        pass
