from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial, reduce
from operator import itemgetter, methodcaller
from typing import TypedDict

from loaders import Record
from models import TransactionRank


class Processed(TypedDict):
    id: int
    type: str
    amount: float
    currency: str
    status: str
    converted: float


def pipeline(value: object, *functions: Callable[[object], object]) -> object:
    return reduce(lambda acc, fn: fn(acc), functions, value)


def normalize(record: Record) -> Processed:
    strip = methodcaller("strip")
    return {
        "id": int(itemgetter("id")(record)),
        "type": strip(str(record["type"])).lower(),
        "amount": float(str(record["amount"])),
        "currency": strip(str(record["currency"])).upper(),
        "status": strip(str(record["status"])).lower(),
        "converted": 0.0,
    }


def convert(record: Processed, rates: dict[str, float]) -> Processed:
    if record["currency"] not in rates:
        raise ValueError("Unknown currency")
    return {
        **record,
        "converted": round(record["amount"] * rates[record["currency"]], 2),
    }


def valid(record: Processed, status: str) -> bool:
    return record["status"] == status


def process_records(
    records: Iterable[Record],
    *,
    rates: dict[str, float],
    status: str = "success",
    top: int = 3,
) -> list[Processed]:
    if top < 0:
        raise ValueError("Top must be nonnegative")
    normalize_all = partial(map, normalize)
    filter_status = partial(filter, partial(valid, status=status))

    def convert_all(rows: Iterable[Processed]) -> Iterable[Processed]:
        return map(partial(convert, rates=rates), rows)

    def collect(rows: Iterable[Processed]) -> list[Processed]:
        return sorted(rows, key=lambda row: (-row["converted"], row["id"]))[:top]

    normalized = normalize_all(records)
    filtered = filter_status(normalized)
    return collect(convert_all(filtered))


def totals(records: Iterable[Processed]) -> dict[str, float | int]:
    rows = tuple(records)
    total: float = reduce(lambda acc, row: float(acc) + row["converted"], rows, 0.0)
    return {"count": len(rows), "amount": round(total, 2)}


def rank(records: Iterable[Processed]) -> list[TransactionRank]:
    return sorted(
        (TransactionRank(row["id"], row["converted"]) for row in records), reverse=True
    )
