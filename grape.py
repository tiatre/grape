import networkx as nx
from collections import defaultdict

# TODO: Work on dynamic resolution adjustment


def build_language_graph(data):
    # Extract languages and concepts from keys
    languages = set()
    concepts = set()
    for lang, concept in data.keys():
        languages.add(lang)
        concepts.add(concept)

    # Prepare to count cognatesets shared between language pairs for each concept
    concept_lang_cognatesets = defaultdict(lambda: defaultdict(set))

    # Fill the structure with available data
    for (lang, concept), cognatesets in data.items():
        concept_lang_cognatesets[concept][lang] = cognatesets

    # Create a structure to hold weights of edges between languages
    language_pairs = defaultdict(int)

    # Calculate weights for edges by checking shared cognatesets
    for concept in concepts:
        # Get languages for this concept
        concept_languages = concept_lang_cognatesets[concept]

        # Compare each pair of languages
        lang_list = list(concept_languages.keys())
        for i in range(len(lang_list)):
            for j in range(i + 1, len(lang_list)):
                lang1 = lang_list[i]
                lang2 = lang_list[j]
                # Find intersection of cognatesets and increment weight for the pair
                shared_cognatesets = concept_lang_cognatesets[concept][
                    lang1
                ].intersection(concept_lang_cognatesets[concept][lang2])
                if shared_cognatesets:
                    language_pairs[(lang1, lang2)] += len(shared_cognatesets)
                    language_pairs[(lang2, lang1)] += len(shared_cognatesets)

    # Create the graph
    G = nx.Graph()

    # Add nodes
    for language in languages:
        G.add_node(language)

    # Add weighted edges based on shared cognatesets
    for (lang1, lang2), weight in language_pairs.items():
        if weight > 0:
            G.add_edge(lang1, lang2, weight=weight)

    return G


def read_cognates(input_file):
    cognates_dict = {}

    with open(input_file, "r") as f_in:
        # Skip the header line
        next(f_in)

        # Process each line in the input file
        for line in f_in:
            # Split the line by tabs
            lang, concept, cognateset = line.strip().split("\t")

            # Skip if cognateset is empty
            if not cognateset:
                continue

            # Remove the concept and language from cognateset
            cognateset = int(cognateset.split(".")[1])

            # Create a tuple of language and concept
            key = (lang, concept)

            # Add cognateset to the set for the corresponding language-concept pair
            if key not in cognates_dict:
                cognates_dict[key] = set()
            cognates_dict[key].add(cognateset)

    return cognates_dict


def build_history(G, num_languages):
    # Iterate with different resolutions
    resolution = 0.0
    history = []
    while True:
        resolution += 0.1

        community_generator = nx.algorithms.community.greedy_modularity_communities(
            G, weight="weight", resolution=resolution
        )
        communities = list(community_generator)
        num_communities = len(communities)

        # If `history` is empty or the number of communities is different from the last element of `history`
        if not history or num_communities != len(history[-1][1]):
            history.append((resolution, communities))
            print(f"Resolution: {resolution:.1f}, Communities: {num_communities}")
            print(communities)

        if num_communities == num_languages:
            break

    return history


from ete3 import Tree, TreeNode


def build_tree_from_history(history):
    """
    Constructs a phylogenetic tree from a provided historical sequence of taxonomic groupings.

    Parameters:
    history (list of tuples): Each tuple contains a resolution (float) and a list of frozensets.
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
    taxa = sorted(taxon for clade in history[-1][1] for taxon in clade)

    # Initialize the last observed ancestor of each taxon to the root of the tree.
    for taxon in taxa:
        last_observed_ancestor[taxon] = tree

    # Iterate through the history, starting from the second tuple to avoid redundancy with the root initialization.
    observed_clades = {}
    for resolution, clades in history[1:]:
        for clade in clades:
            # Create a label for the clade using sorted taxa names to ensure uniqueness and consistency.
            clade_label = ",".join(sorted(clade))

            # Avoid processing the same clade label more than once, but make sure to extend its branch length
            # as long as it is not a single taxon clade.
            if clade_label in observed_clades:
                if len(clade) > 1:
                    observed_clades[clade_label].dist = resolution
                continue

            # Create a new node for the clade; the name will be the taxon label if the clade contains a single taxon,
            # or empty otherwise.
            node = TreeNode(name=clade_label if len(clade) == 1 else "")

            # Connect the new clade node to its ancestor nodes, ensuring no duplicate branches are created.
            branches_added = set()
            for taxon in clade:
                ancestor = last_observed_ancestor[taxon]
                if ancestor not in branches_added:
                    # If the ancestor is the root, the branch length is the resolution itself. Otherwise,
                    # the branch length is the difference between the current resolution and the ancestor's resolution.
                    if ancestor == tree:
                        branch_length = resolution
                    else:
                        # Make sure there is a minimum branch length to avoid zero-length branches.
                        branch_length = max(1e-8, resolution - ancestor.dist)
                    ancestor.add_child(node, dist=branch_length)
                    branches_added.add(ancestor)

                # Update the last observed ancestor for each taxon to the current clade's node.
                last_observed_ancestor[taxon] = node

            # Record this clade label to prevent future reprocessing.
            observed_clades[clade_label] = node

    return tree


import matplotlib.pyplot as plt


def draw_and_save_graph(G):
    plt.figure(figsize=(8, 6))  # Set the size of the image
    nx.draw(
        G,
        with_labels=True,
        node_color="skyblue",
        font_weight="bold",
        node_size=700,
        font_size=9,
    )
    plt.title("Language Graph")
    plt.savefig("language_graph.png")  # Save the graph to a file
    plt.close()  # Close the plot to free up memory


def main():
    cognates = read_cognates("ie.tsv")
    print(cognates[("English", "ANT")])

    # Obtain the number of languages and concepts
    num_languages = len(set([lang for lang, _ in cognates.keys()]))
    num_concepts = len(set([concept for _, concept in cognates.keys()]))

    # Print the contents of the dictionary
    for key, value in cognates.items():
        print(key, ":", value)

    G = build_language_graph(cognates)
    print(G.edges(data=True))

    history = build_history(G, num_languages)
    print(len(history))

    tree = build_tree_from_history(history)
    print(tree)

    # Print the tree in Newick format, with internal node names and branch lengths
    print(tree.write(format=1))


if __name__ == "__main__":
    main()
