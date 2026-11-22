from pathlib import Path

from core import process_records, rank, totals
from loaders import load_transactions


def main() -> None:
    source = Path(__file__).resolve().parent / "data" / "sample_data.json"
    result = process_records(
        load_transactions(source), rates={"UAH": 1.0, "USD": 40.0, "EUR": 43.0}
    )
    print("Лабораторна №7 — банківські транзакції, варіант 10")
    for item in result:
        print(f"#{item['id']}: {item['converted']:.2f} грн ({item['currency']})")
    print("Агрегація:", totals(result))
    print("Рейтинг:", rank(result))


if __name__ == "__main__":
    main()
