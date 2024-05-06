from dataclasses import dataclass
from functools import cached_property

from typing import List, FrozenSet, Dict, Set, Tuple


@dataclass
class HistoryEntry:
    """Class to store a history entry with resolution and communities.

    Attributes:
        parameter (float): The resolution value indicating the distance to the root.
        communities (List[FrozenSet[str]]): A list of communities, each represented as a frozenset of strings.
    """

    parameter: float
    communities: List[FrozenSet[str]]

    @cached_property
    def number_of_communities(self) -> int:
        """Returns the number of communities in this history entry, caching the result."""
        return len(self.communities)
