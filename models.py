from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, eq=False, slots=True)
class TransactionRank:
    id: int
    amount: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TransactionRank):
            return NotImplemented
        return (self.amount, -self.id) == (other.amount, -other.id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TransactionRank):
            return NotImplemented
        return (self.amount, -self.id) < (other.amount, -other.id)
