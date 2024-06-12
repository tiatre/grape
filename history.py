import networkx as nx
from typing import List, Callable, Dict, Any, Tuple, FrozenSet
from common import HistoryEntry

from typing import List


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


class AdaptiveDynamicAdjustmentStrategy(ParameterSearchStrategy):
    def __init__(
        self,
        initial_value: float = 0.1,
        adjust_factor: float = 0.05,
        target: int = None,
    ):
        self.initial_value = initial_value
        self.adjust_factor = adjust_factor
        self.target = target
        self.value = initial_value
        self.previous_diff = None

    def initialize(self) -> float:
        return self.initial_value

    def update(self, current_value: float, current_communities: int) -> float:
        # Calculate the difference between the current number of communities and the target
        diff = abs(self.target - current_communities)

        # If this is the first update, initialize previous_diff
        if self.previous_diff is None:
            self.previous_diff = diff
            return current_value

        # Check if the number of communities is moving towards the target or not
        if diff < self.previous_diff:
            # We are getting closer to the target, increase the adjustment factor slightly
            self.adjust_factor *= 1.1
        else:
            # We are moving away from the target, decrease the adjustment factor and change direction
            self.adjust_factor *= -0.5

        self.previous_diff = diff
        self.value += self.adjust_factor
        return self.value

    def should_stop(self, num_communities: int, target: int) -> bool:
        return num_communities == target


def split_sets(list1: List[set], list2: List[set]) -> List[set]:
    """
    Split the sets in list2 into smaller sets that match the sets in list1.

    Each set in list2 is broken down into subsets such that each subset can be completely
    found within at least one set in list1. This helps in ensuring that elements of each
    split set from list2 align with elements from a complete set in list1.

    Parameters:
    list1 (List[Set[Any]]): A list of sets representing the main groups of elements.
    list2 (List[Set[Any]]): A list of sets which need to be split according to the groups in list1.

    Returns:
    List[Set[Any]]: A list of sets where each set from list2 is split into subsets that match the sets in list1.

    Example:
    list1 = [{0, 1, 2, 3},   {4, 5}, {6, 7, 8}]
    list2 = [{1, 2}, {3}, {4, 5, 6}, {0, 7, 8}]

    The result will be [{1, 2}, {3}, {4, 5}, {6}, {0}, {7, 8}], where each subset from list2 is found within a set from list1.
    """

    # Initialize the result
    result = []

    # Iterate over each set in list2 and split it into subsets that match the sets in list1
    for set2 in list2:
        sub_result = []
        for set1 in list1:
            intersection = set2 & set1
            if intersection:
                sub_result.append(intersection)
        result.append(sub_result)

    # Flatten the result before returning
    result = [item for sublist in result for item in sublist]

    return result


def build_history(
    G: nx.Graph,
    num_languages: int,
    method: str = "greedy",
    strategy: str = "fixed",
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
        "fixed": FixedIncrementStrategy(),
        "dynamic": DynamicAdjustmentStrategy(
            initial_value=initial_value, adjust_factor=adjust_factor
        ),
        "adaptive": AdaptiveDynamicAdjustmentStrategy(
            initial_value=initial_value,
            adjust_factor=adjust_factor,
            target=num_languages,
        ),
    }.get(strategy)
    if strategy is None:
        raise ValueError("Unsupported parameter search strategy")

    history = []
    parameter = strategy.initialize()

    while True:
        identified_communities = community_method.find_communities(resolution=parameter)

        # After obtaining the communities, we must make sure that the new communities do not contradict the
        # previous ones, as the algorithm might group at this level taxa that were separated in the
        # previous one (this is a common issue in some hierarchical clustering algorithms).
        if not history:
            # First level
            communities = identified_communities
        else:
            communities = split_sets(history[-1].communities, identified_communities)

        num_communities = len(communities)

        # Store the history entry if the number of communities has increased (depending on the algorithm and the parameters,
        # the number of communities may decrease in some iterations))
        if not history or num_communities > history[-1].number_of_communities:
            history_entry = HistoryEntry(parameter, communities)
            history.append(history_entry)
            print(f"Parameter: {parameter:.2f}, Communities: {num_communities}")

        if strategy.should_stop(num_communities, num_languages):
            break

        parameter = strategy.update(parameter)

    return history
