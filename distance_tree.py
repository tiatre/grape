import numpy as np
from ete3 import Tree
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor


def distance_tree(distance_matrix, taxa, method):
    """
    Performs the Neighbor-Joining algorithm on a distance matrix and a list of taxa names.
    Returns an ETE3 tree object.
    """
    # method must be one of 'nj' or 'upgma'
    if method not in ["nj", "upgma"]:
        raise ValueError("method must be 'nj' or 'upgma'")

    # Convert the distance matrix to a Bio.Phylo DistanceMatrix object
    # (this is done by creating a data structure with the lower triangular part of the matrix, e.g.
    # matrix=`[[0], [0.23, 0], [0.38, 0.23, 0]` instead of `[[0, 0.23, 0.38], [0.23, 0, 0.23], [0.38, 0.23, 0]]`)
    lower_triangle = []
    for i in range(len(distance_matrix)):
        lower_triangle.append(list(distance_matrix[i, : i + 1]))
    dm = DistanceMatrix(taxa, lower_triangle)

    # Perform neighbor joining
    constructor = DistanceTreeConstructor()
    if method == "upgma":
        tree = constructor.upgma(dm)
    else:
        tree = constructor.nj(dm)

    # Convert the Bio.Phylo tree to an ETE3 tree
    newick = tree.format("newick")
    ete_tree = Tree(newick, format=1)

    return ete_tree


def nj(distance_matrix, taxa):
    """
    Performs the Neighbor-Joining algorithm on a distance matrix and a list of taxa names.
    Returns an ETE3 tree object.
    """
    return distance_tree(distance_matrix, taxa, "nj")


def upgma(distance_matrix, taxa):
    """
    Performs the UPGMA algorithm on a distance matrix and a list of taxa names.
    Returns an ETE3 tree object.
    """
    return distance_tree(distance_matrix, taxa, "upgma")


# Example distance matrix
distance_matrix = np.array(
    [[0, 0.5, 0.8, 0.9], [0.5, 0, 0.7, 0.8], [0.8, 0.7, 0, 0.6], [0.9, 0.8, 0.6, 0]]
)

# Example list of taxa names
taxa_names = ["A", "B", "C", "D"]

# Call the neighbor joining function
tree = nj(distance_matrix, taxa_names)
print(tree.write(format=1))

# Call the UPGMA function
tree = upgma(distance_matrix, taxa_names)
print(tree.write(format=1))
