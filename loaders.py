from __future__ import annotations

import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import cast

Record = dict[str, object]


def parse_records(text: str, *, csv_mode: bool = False) -> list[Record]:
    if csv_mode:
        return [dict(row) for row in csv.DictReader(io.StringIO(text))]
    data = json.loads(text)
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("Expected a JSON list of objects")
    return cast(list[Record], data)


@singledispatch
def load_transactions(source: object) -> list[Record]:
    raise TypeError(f"Unsupported source: {type(source).__name__}")


@load_transactions.register
def _(source: str) -> list[Record]:
    stripped = source.strip()
    if stripped.startswith("["):
        return parse_records(stripped)
    if "\n" in stripped and "," in stripped:
        return parse_records(stripped, csv_mode=True)
    return load_transactions(Path(source))


@load_transactions.register
def _(source: Path) -> list[Record]:
    return parse_records(
        source.read_text(encoding="utf-8"), csv_mode=source.suffix.lower() == ".csv"
    )


@load_transactions.register
def _(source: io.TextIOBase) -> list[Record]:
    text = source.read()
    return parse_records(
        text,
        csv_mode=(
            source.name.endswith(".csv")
            if hasattr(source, "name")
            else not text.lstrip().startswith("[")
        ),
    )


@load_transactions.register(list)
def _(source: list[Record]) -> list[Record]:
    return [dict(row) for row in source]
