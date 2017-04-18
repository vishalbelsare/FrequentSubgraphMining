
import source.graph as graph_module
from source.fragment import Fragment
from source.level import Level

class Node(Fragment):
    """ A fragment containing a node subgraph. """

    def __init__(self, source_node_id, source_graph):

        node_label = source_graph.node[source_node_id]['label']
        current_graph = graph_module.create_nx_node_graph(source_node_id, node_label)

        embedding_list = tuple([node_label])

        super().__init__(source_node_id, current_graph, source_graph, embedding_list)

    def __str__(self):
        return "Node"

    @property
    def queue_level(self):
        """ A property to specify the search queue containing node fragments. """
        return Level.NODE
    