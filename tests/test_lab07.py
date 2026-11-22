from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from core import normalize, pipeline, process_records, rank, totals
from loaders import load_transactions
from models import TransactionRank

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"


def test_load_all_sources() -> None:
    text = DATA.read_text(encoding="utf-8")
    expected = load_transactions(text)
    assert load_transactions(DATA) == expected
    assert load_transactions(str(DATA)) == expected
    assert load_transactions(io.StringIO(text)) == expected
    assert load_transactions(expected) == expected
    csv_path = DATA.with_suffix(".csv")
    assert len(load_transactions(csv_path)) == len(expected)
    assert len(load_transactions(csv_path.read_text(encoding="utf-8"))) == len(expected)
    assert len(
        load_transactions(io.StringIO(csv_path.read_text(encoding="utf-8")))
    ) == len(expected)


def test_pipeline() -> None:
    assert pipeline(2, lambda n: int(str(n)) + 1, lambda n: int(str(n)) * 3) == 9
    assert pipeline("same") == "same"


def test_normalize_and_operator() -> None:
    assert normalize(
        {
            "id": "1",
            "type": " Deposit ",
            "amount": "5",
            "currency": " usd ",
            "status": " SUCCESS ",
        }
    ) == {
        "id": 1,
        "type": "deposit",
        "amount": 5.0,
        "currency": "USD",
        "status": "success",
        "converted": 0.0,
    }


def test_processing_and_immutability() -> None:
    original = load_transactions(DATA)
    before = json.dumps(original, sort_keys=True)
    result = process_records(original, rates={"USD": 40.0, "EUR": 43.0, "UAH": 1.0})
    assert [row["id"] for row in result] == [103, 104, 101]
    assert [row["converted"] for row in result] == [1075.0, 900.0, 800.0]
    assert totals(result) == {"count": 3, "amount": 2775.0}
    assert json.dumps(original, sort_keys=True) == before
    assert [x.id for x in rank(result)] == [103, 104, 101]


def test_boundaries() -> None:
    assert process_records([], rates={}, top=0) == []
    assert totals([]) == {"count": 0, "amount": 0.0}
    with pytest.raises(ValueError):
        process_records([], rates={}, top=-1)
    with pytest.raises(ValueError):
        process_records(
            [
                {
                    "id": 1,
                    "type": "a",
                    "amount": 1,
                    "currency": "XYZ",
                    "status": "success",
                }
            ],
            rates={},
        )


def test_ordering() -> None:
    first = TransactionRank(1, 500.0)
    second = TransactionRank(2, 500.0)
    third = TransactionRank(3, 700.0)
    assert first > second
    assert first >= second
    assert second < first
    assert second <= first
    assert third > first
    assert first == TransactionRank(1, 500.0)
    assert first != third
    assert first.__lt__("wrong") is NotImplemented
    assert first.__eq__("wrong") is NotImplemented
