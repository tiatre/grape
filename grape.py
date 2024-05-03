import networkx as nx
from collections import defaultdict


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


def main():
    cognates = read_cognates("ie.tsv")
    print(cognates[("English", "ANT")])

    # Print the contents of the dictionary
    for key, value in cognates.items():
        print(key, ":", value)

    G = build_language_graph(cognates)
    print(G.edges(data=True))


if __name__ == "__main__":
    main()
