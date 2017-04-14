class Path(object):
    def __init__(self, start_node_id, back_node_id, current_graph, 
                     source_graph, embedding_list, 
                     total_symmetry, front_symmetry, back_symmetry):
        self.start_node_id, self.back_node_id, self.current_graph = start_node_id, back_node_id, current_graph
        self.source_graph, self.embedding_list = source_graph, embedding_list
        self.total_symmetry, self.front_symmetry, self.back_symmetry = total_symmetry, front_symmetry, back_symmetry

    @property
    def frontier_edges(self):
        for node_id in self.current_graph:
            edges = self.current_graph.edge[node_id]
            for neighbor_id in self.source_graph.neighbors_iter(node_id):
                if neighbor_id not in edges:
                    yield (node_id, neighbor_id)
    
    @property
    def symmetries(self):
        return (self.total_symmetry, self.front_symmetry, self.back_symmetry)

    @staticmethod
    def compute_symmetry(embedding_list, reversed_list=None):
        """ O(n) method for calculating the symmetry  """
        if reversed_list is None:
            reversed_list = tuple(reversed(embedding_list))
        return 0 if embedding_list == reversed_list else 1 if embedding_list < reversed_list else -1

    # @staticmethod
    # def new_path_symmetries(prev_symmetries, edge1, new_edge):
        
        # old_total, old_front, old_back = prev_symmetries

        # O(1) method is direction dependent (needs to be changed if used for prepending)
        # new_front = old_total
        # if old_back == 0:
        #     new_total = 1 if edge1 < new_edge else 0 if edge1 == new_edge else -1
        # elif old_back == 1:
        #     new_total = 1 if edge1 <= new_edge else -1

        # new_back = calculate new back

        # return (new_total, new_front, new_back)

    @staticmethod
    def new_path_symmetries(embedding_list):
        # slower methods being used to ensure correctness
        reversed_list = tuple(reversed(embedding_list))

        new_front = Path.compute_symmetry(embedding_list[:-2], reversed_list[:-2])
        new_total = Path.compute_symmetry(embedding_list, reversed_list)
        new_back = Path.compute_symmetry(embedding_list[2:], reversed_list[2:])

        return (new_total, new_front, new_back)