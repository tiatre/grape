from ete3 import Tree, TreeNode
from typing import List, Dict, FrozenSet
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


def build_tree_from_history(history: List[HistoryEntry]) -> TreeNode:
    """
    Constructs a phylogenetic tree from a provided historical sequence of taxonomic groupings.

    Parameters:
    history (List[HistoryEntry]): Each HistoryEntry contains a resolution (float) and a list of frozensets.
        The resolution indicates the cumulative distance from the root of the tree,
        while each frozenset contains names of taxa that form a clade at this resolution.
        The history is expected to be sorted with resolution values increasing (from root to leaves),
        with the most granular resolution (individual taxa) last.

    Returns:
    TreeNode: The root node of the constructed ete3 phylogenetic tree.

    Notes:
    - The function assumes that the resolutions in the history are strictly increasing.
    - Polytomies (clades branching into more than two taxa) are handled naturally.
    """

    # Return an empty node if history is empty

    if not history:
        return TreeNode()

    # Initialize the root TreeNode.
    tree_root = Tree()
    node_resolutions: Dict[TreeNode, float] = {tree_root: 0.0}

    last_observed_ancestor: Dict[str, TreeNode] = {}

    # Extract all unique taxa from the most granular level of the history.
    if history[-1].communities:
        taxa = sorted(
            list(set(taxon for clade in history[-1].communities for taxon in clade))
        )
    else:
        taxa = []  # Should not happen with valid history leading to taxa

    for taxon in taxa:
        last_observed_ancestor[taxon] = tree_root

    observed_clades: List[FrozenSet[str]] = []

    # Iterate through the entire history to build the tree structure.
    for entry in history:  # Process all entries, including history[0]
        current_entry_resolution = entry.parameter
        clades_in_entry = entry.communities

        for clade_members in clades_in_entry:
            if not clade_members:  # Skip empty clades if they occur
                continue
            if clade_members in observed_clades:
                continue

            clade_label = "/".join(sorted(list(clade_members)))
            new_node = TreeNode(name=clade_label)
            node_resolutions[new_node] = current_entry_resolution

            # Determine the parent node for this new_node.
            # All members of the clade_members set should share the same last_observed_ancestor.
            potential_parents = {
                last_observed_ancestor[member]
                for member in clade_members
                if member in last_observed_ancestor
            }

            actual_parent_node: TreeNode
            if not potential_parents:
                # This implies taxa in clade_members were not in last_observed_ancestor map.
                # This could happen if history is malformed or taxa are introduced mid-history without prior record.
                # Defaulting to tree_root or raising error are options.
                # For now, we assume valid history means this path is less likely for non-root clades.
                # If current_entry_resolution is the first one, parent is tree_root.
                if current_entry_resolution == history[0].parameter:
                    actual_parent_node = tree_root
                else:
                    # This is an unexpected state for a non-root clade.
                    raise ValueError(
                        f"Clade '{clade_label}' at resolution {current_entry_resolution} has no identifiable parent. Taxa: {clade_members}"
                    )
            elif len(potential_parents) > 1:
                parent_names = sorted([p.name for p in potential_parents])
                raise ValueError(
                    f"Clade '{clade_label}' at resolution {current_entry_resolution} has multiple potential parents: "
                    f"{parent_names} ({len(potential_parents)}). This indicates inconsistent history."
                )
            else:
                actual_parent_node = potential_parents.pop()

            # Add the new node as a child of its parent. Default to 0 if parent not in map (e.g. root)
            parent_resolution = node_resolutions.get(actual_parent_node, 0.0)
            branch_length = max(1e-8, node_resolutions[new_node] - parent_resolution)
            actual_parent_node.add_child(new_node, dist=branch_length)

            observed_clades.append(clade_members)

            # Update last_observed_ancestor for all members of this new clade.
            for member in clade_members:
                last_observed_ancestor[member] = new_node

    # Post-processing: Prune unary nodes.
    final_tree_root = remove_single_descendant_nodes(tree_root)

    # Clean up internal node names and temporary features.
    for node in final_tree_root.traverse("postorder"):  # type: ignore
        if not node.is_leaf():
            node.name = ""

    final_tree_root.sort_descendants()
    final_tree_root.ladderize()

    return final_tree_root
