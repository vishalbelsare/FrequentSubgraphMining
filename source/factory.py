
from collections import namedtuple
from source.node import Node
from source.path import Path
from source.tree import Tree
from source.cycle import Cycle
import source.helper as helper
import source.embedding as embedding

def initial_nodes(graphs):
    return [Node(node_id, source_graph) for source_graph in graphs for node_id in source_graph]

def apply_refinement(gaston_obj, edge):
    """"""
    origin_id, target_id = edge

    if isinstance(gaston_obj, Node):
        return _create_path_from_node(gaston_obj, target_id)
    
    elif target_id in gaston_obj.current_graph:
        return _create_cycle(gaston_obj, origin_id, target_id)
    
    elif isinstance(gaston_obj, Path):
        if origin_id == gaston_obj.back_node_id:
            return _append_to_path(gaston_obj, target_id)
    
        elif origin_id == gaston_obj.start_node_id:
            _prepend_node_to_path(gaston_obj, target_id)
            # return None
    
        else:
            return _create_tree_from_path(gaston_obj, origin_id, target_id)

    elif isinstance(gaston_obj, Tree):
        return _create_tree_from_tree(gaston_obj, origin_id, target_id)

def _create_path_from_node(gaston_node, appending_node_id):
    start_node_id, frontier_edges, source_graph = gaston_node

    start_node_label = source_graph.node[start_node_id]['label']
    appending_node_label = source_graph.node[appending_node_id]['label']
    edge_label = source_graph.edge[start_node_id][appending_node_id]['label']

    # Check if refinement is allowed
    if appending_node_label < start_node_label:
        return None

    current_graph = helper.create_nx_graph(start_node_id, start_node_label, 
                                            appending_node_id, appending_node_label, 
                                            edge_label)

    # Find the embedding that begins at the previous path's back node
    # The alt embedding beginning from the new back node will be created from a different fragment
    embedding_list = embedding.create_embedding_list_if_unique(current_graph, 
                                                               source_id=start_node_id, 
                                                               alt_source_id=appending_node_id)
    if embedding_list is None:
        return None

    # total_symmetry = 0 if appending_node_label == start_node_label else 1
    
    return Path(start_node_id, appending_node_id, current_graph, 
                source_graph, embedding_list, 
                total_symmetry=0, front_symmetry=0, back_symmetry=0)

def _append_to_path(prev_path, new_back_id):

    target_node_label = prev_path.source_graph.node[new_back_id]['label']
    target_edge_label = prev_path.source_graph.edge[prev_path.back_node_id][new_back_id]['label']

    # edge1 = tuple(prev_path.embedding_list[:2]) # (l(v1), l(e1))
    # new_edge = (target_node_label, target_edge_label)
    # embedding_list = prev_path.embedding_list + (target_edge_label, target_node_label)

    # Needs to be changed if using the O(1) method for finding new path symmetries
    # total_symmetry, front_symmetry, back_symmetry = Path.new_path_symmetries(embedding_list)

    # Check if refinement is allowed
    # append is allowed if total_symmetry == 0
    # (l(v'), l(e')) > (l(v1), l(e1))
    # if (l(v'), l(e')) == (l(v1), l(e1)) and back_symmetry >= 0

    # if total_symmetry == -1 or edge1 == new_edge and back_symmetry == -1:
    #     return None

    current_graph = helper.extend_nx_graph(prev_path.current_graph, prev_path.back_node_id, new_back_id, 
                                           target_node_label, target_edge_label)

    # Find the embedding that begins at the previous path's back node
    # The alt embedding beginning from the new back node will be created from a different fragment
    embedding_list = embedding.create_embedding_list_if_unique(current_graph, 
                                                               source_id=prev_path.start_node_id, 
                                                               alt_source_id=new_back_id)
    if embedding_list is None:
        return None
    
    return Path(prev_path.start_node_id, new_back_id, current_graph, 
                prev_path.source_graph, embedding_list, 
                total_symmetry=0, front_symmetry=0, back_symmetry=0)


def _prepend_node_to_path(prev_path, new_start_node_id):

    new_node_label = prev_path.source_graph.node[new_start_node_id]['label']
    new_edge_label = prev_path.source_graph.edge[new_start_node_id][prev_path.start_node_id]['label']

    # edge1 = tuple(prev_path.embedding_list[:2]) # (l(v1), l(e1))
    # new_edge = (new_node_label, new_edge_label)
    # embedding_list = new_edge + prev_path.embedding_list

    # Needs to be changed if using the O(1) method for finding new path symmetries
    # total_symmetry, front_symmetry, back_symmetry = Path.new_path_symmetries(embedding_list)

    # Check if refinement is allowed
    # append is allowed if total_symmetry == 1
    # (l(v'), l(e')) > (l(v1), l(e1))
    # if (l(v'), l(e')) == (l(v1), l(e1)) and back_symmetry >= 0

    # if total_symmetry != 1 or edge1 == new_edge and back_symmetry == -1:
    #     return None

    # Incorrect order if graph is directed
    current_graph = helper.extend_nx_graph(prev_path.current_graph, prev_path.start_node_id, new_start_node_id, 
                                           new_node_label, new_edge_label)
    
    # Find the embedding that begins at the previous path's start node
    # The alt embedding beginning from the new start node will be created from a different fragment
    embedding_list = embedding.create_embedding_list_if_unique(current_graph, 
                                                               source_id=prev_path.start_node_id, 
                                                               alt_source_id=new_start_node_id)
    if embedding_list is None:
        return None
    
    return Path(new_start_node_id, prev_path.back_node_id, current_graph, 
                prev_path.source_graph, embedding_list, 
                total_symmetry=0, front_symmetry=0, back_symmetry=0)

def _create_tree_from_path(prev_path, origin_id, target_id):
    root_node_id = prev_path.start_node_id
    return _create_tree(prev_path.source_graph, prev_path.current_graph, 
                        root_node_id, prev_path.frontier_edges, 
                        origin_id, target_id)

def _create_tree_from_tree(prev_tree, origin_id, target_id):
    return _create_tree(prev_tree.source_graph, prev_tree.current_graph, 
                        prev_tree.root_node_id, prev_tree.frontier_edges, 
                        origin_id, target_id)

def _create_tree(source_graph, prev_graph, root_id, prev_frontier_edges, origin_id, target_id):
    
    new_node_label = source_graph.node[target_id]['label']
    new_edge_label = source_graph.edge[origin_id][target_id]['label']

    current_graph = helper.extend_nx_graph(prev_graph, origin_id, target_id, 
                                           new_node_label, new_edge_label)

    embedding_list = embedding.create_embedding_list_if_unique(current_graph, 
                                                               source_id=root_id, 
                                                               alt_source_id=target_id)
    if embedding_list is None:
        return None

    return Tree(root_id, current_graph, source_graph, embedding_list)

def _create_cycle(gaston_obj, origin_id, target_id):

    source_graph, prev_graph = gaston_obj.source_graph, gaston_obj.current_graph

    if isinstance(gaston_obj, Path):
        if target_id == gaston_obj.start_node_id:
            return None
        source_node_id = gaston_obj.start_node_id
    elif isinstance(gaston_obj, Tree):
        source_node_id = gaston_obj.root_node_id
    elif isinstance(gaston_obj, Cycle):
        source_node_id = gaston_obj.source_node_id

    new_node_label = source_graph.node[target_id]['label']
    new_edge_label = source_graph.edge[origin_id][target_id]['label']

    current_graph = helper.extend_nx_graph(prev_graph, origin_id, target_id, 
                                           new_node_label, new_edge_label)

    embedding_list = embedding.create_embedding_list_if_unique(current_graph, 
                                                               source_id=source_node_id, 
                                                               alt_source_id=target_id)
    if embedding_list is None:
        return None

    return Cycle(source_node_id, current_graph, source_graph, embedding_list)
