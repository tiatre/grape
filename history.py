import networkx as nx

from typing import List, FrozenSet, Dict, Set, Tuple

from common import HistoryEntry
from networkx.algorithms.community import (
    greedy_modularity_communities,
    louvain_communities,
)
import itertools

# TODO: Work on dynamic resolution adjustment


def build_history(G, num_languages, method="greedy"):
    history = []
    parameter = 0.0

    if method == "greedy":
        # Use Greedy Modularity method
        while True:
            parameter += 0.1

            community_generator = greedy_modularity_communities(
                G, weight="weight", resolution=parameter
            )
            communities = [frozenset(community) for community in community_generator]
            num_communities = len(communities)

            if not history or num_communities != history[-1].number_of_communities:
                history_entry = HistoryEntry(parameter, communities)
                history.append(history_entry)
                print(f"Parameter: {parameter:.1f}, Communities: {num_communities}")
                print(communities)

            if num_communities == num_languages:
                break
    elif method == "louvain_communities":
        # Use Louvain method
        while True:
            parameter += 0.1

            community_generator = louvain_communities(
                G, weight="weight", resolution=parameter
            )
            communities = [frozenset(community) for community in community_generator]
            num_communities = len(communities)

            if not history or num_communities != history[-1].number_of_communities:
                history_entry = HistoryEntry(parameter, communities)
                history.append(history_entry)
                print(f"Parameter: {parameter:.1f}, Communities: {num_communities}")
                print(communities)

            if num_communities == num_languages:
                break

    return history
