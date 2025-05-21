from ete3 import Tree, TreeNode
from typing import List
from common import HistoryEntry


def remove_single_descendant_nodes(tree: TreeNode) -> TreeNode:
    """
    Removes nodes with a single descendant from an ete3 TreeNode.

    When a node with a single child is removed (a "unary" node), its child is
    connected directly to the unary node's parent (grandparent). Branch lengths
    (dist attribute) are adjusted: the child's new dist becomes the sum of its
    original dist and the dist of the removed unary node.

    If the root node itself has only one child after internal pruning, it is
    also removed, and its child becomes the new root. The new root's 'dist'
    attribute will be set to 0.

    @param tree: The root TreeNode of the tree to be pruned.
    @return: The root TreeNode of the pruned tree. This might be a different
             node if the original root was pruned.
    """

    def prune_node(node: TreeNode):
        # We use a stack to manage nodes to check (iterative depth-first)
        stack = [node]
        while stack:
            current_node = stack.pop()
            # Iterate over children list while modifying it (use a copy)
            for child_node in current_node.get_children():
                stack.append(child_node)

            # If the node has exactly one child and it's not the root
            if len(current_node.children) == 1 and current_node.up is not None:
                child = current_node.children[0]
                # Update the child's distance from its new parent (the grandparent)
                child.dist += current_node.dist

                # Connect the child directly to the grandparent
                current_node.up.add_child(child, dist=child.dist)

                # Remove the current node (which also removes it from its parent's children list)
                current_node.up.remove_child(current_node)

    # Start processing from the root
    current_root_node = tree
    prune_node(current_root_node)

    # Check if the root itself needs pruning
    if len(current_root_node.children) == 1 and not current_root_node.is_leaf():
        new_root = current_root_node.children[0]
        new_root.detach()  # Detach new_root from old_root; new_root.up becomes None.
        new_root.dist = 0.0
        current_root_node = new_root

    return current_root_node


def build_tree_from_history(history: List[HistoryEntry]):
    """
    Constructs a phylogenetic tree from a provided historical sequence of taxonomic groupings.

    Parameters:
    history (List[HistoryEntry]): Each HistoryEntry contains a resolution (float) and a list of frozensets.
        The resolution indicates the cumulative distance from the root of the tree,
        while each frozenset contains names of taxa that form a clade at this resolution.
        The history is expected to be sorted from the most distant from the root to the closest,
        with the most granular resolution (individual taxa) last.

    Returns:
    Tree: An ete3 Tree object representing the constructed phylogenetic tree.

    Notes:
    - The function assumes that the resolutions in the history are strictly increasing as the
      history progresses from the start (root) to the end (leaves).
    - Polytomies (clades branching into more than two taxa) are handled naturally by this approach.
    """

    # Initialize an empty ete3 Tree object.
    tree = Tree()
    last_observed_ancestor = {}

    # Extract all taxa from the last element in history, which contains the most granular clades (individual taxa).
    taxa = sorted(taxon for clade in history[-1].communities for taxon in clade)

    # Initialize the last observed ancestor of each taxon to the root of the tree.
    for taxon in taxa:
        last_observed_ancestor[taxon] = tree

    # Iterate through the history, starting from the second entry to avoid redundancy with the root initialization.
    observed_clades = []
    for entry in history[1:]:
        resolution, clades = entry.parameter, entry.communities

        for clade in clades:
            if clade in observed_clades:
                continue

            # Create a label for the clade using sorted taxa names to ensure uniqueness and consistency.
            clade_label = "/".join(sorted(clade))
            node = TreeNode(name=clade_label)

            ancestor_nodes = {last_observed_ancestor[taxon] for taxon in clade}
            # assert len(ancestor_nodes) == 1, "Clade must have a single common ancestor"

            # Add the new clade node to the list of observed clades, so we don't process it again
            # (this is necesssary for cases where the same clade appears multiple times in the history, because it
            #  will only be resolved at a higher resolution).
            observed_clades.append(clade)

            # Connect the new clade node to the ancestor node, using the resolution as the branch length.
            ancestor_node = ancestor_nodes.pop()
            branch_length = max(1e-8, resolution - ancestor_node.dist)
            ancestor_node.add_child(node, dist=branch_length)

            # Update the last observed ancestor for each taxon to the current clade's node.
            for taxon in clade:
                last_observed_ancestor[taxon] = node

    # Remove single-child nodes from the tree to simplify the representation.
    tree = remove_single_descendant_nodes(tree)

    # Remove the name of all internal nodes to make the tree more readable.
    for node in tree.traverse():  # type: ignore
        if not node.is_leaf():
            node.name = ""

    # Sort the tree in descending order of the number of descendants at each node and ladderize it.
    tree.sort_descendants()
    tree.ladderize()

    return tree
