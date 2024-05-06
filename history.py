import networkx as nx
from typing import List, Callable, Dict, Any, Tuple, FrozenSet
from common import HistoryEntry


class CommunityMethod:
    def __init__(self, graph: nx.Graph, weight: str):
        self.graph = graph
        self.weight = weight

    def find_communities(self, resolution: float) -> List[FrozenSet]:
        raise NotImplementedError("This method should be overridden by subclasses")


class GreedyModularity(CommunityMethod):
    def find_communities(self, resolution: float) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.greedy_modularity_communities(
            self.graph, weight=self.weight, resolution=resolution
        )
        return [frozenset(community) for community in community_generator]


class LouvainCommunities(CommunityMethod):
    def find_communities(self, resolution: float) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.louvain_communities(
            self.graph, weight=self.weight, resolution=resolution
        )
        return [frozenset(community) for community in community_generator]


class ParameterSearchStrategy:
    def initialize(self) -> float:
        raise NotImplementedError

    def update(self, current_value: float) -> float:
        raise NotImplementedError

    def should_stop(self, num_communities: int, target: int) -> bool:
        raise NotImplementedError


class FixedIncrementStrategy(ParameterSearchStrategy):
    def __init__(self, increment: float = 0.1):
        self.increment = increment

    def initialize(self) -> float:
        return 0.0

    def update(self, current_value: float) -> float:
        return current_value + self.increment

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


class DynamicAdjustmentStrategy(ParameterSearchStrategy):
    def __init__(self, initial_value: float = 0.0, adjust_factor: float = 0.1):
        self.adjust_factor = adjust_factor
        self.value = initial_value

    def initialize(self) -> float:
        return self.value

    def update(self, current_value: float) -> float:
        # Dynamic adjustment logic can be implemented here
        # For simplicity, let's just increment by a variable factor
        self.value += self.adjust_factor * self.value
        return self.value

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


def build_history(
    G: nx.Graph,
    num_languages: int,
    method: str = "greedy",
    strategy: str = "fixed_increment",
    initial_value: float = 0.0,
    adjust_factor: float = 0.1,
) -> List[HistoryEntry]:

    # Obtain the community detection method based on the provided method string
    community_method = {
        "greedy": GreedyModularity(G, weight="weight"),
        "louvain": LouvainCommunities(G, weight="weight"),
    }.get(method)
    if community_method is None:
        raise ValueError("Unsupported community detection method")

    # Obtain the search strategy based on the provided strategy string
    strategy = {
        "fixed_increment": FixedIncrementStrategy(),
        "dynamic_adjustment": DynamicAdjustmentStrategy(
            initial_value=initial_value, adjust_factor=adjust_factor
        ),
    }.get(strategy)
    if strategy is None:
        raise ValueError("Unsupported parameter search strategy")

    history = []
    parameter = strategy.initialize()

    while True:
        communities = community_method.find_communities(resolution=parameter)
        num_communities = len(communities)

        if not history or num_communities != history[-1].number_of_communities:
            history_entry = HistoryEntry(parameter, communities)
            history.append(history_entry)
            print(f"Parameter: {parameter:.2f}, Communities: {num_communities}")

        if strategy.should_stop(num_communities, num_languages):
            break

        parameter = strategy.update(parameter)

    return history
