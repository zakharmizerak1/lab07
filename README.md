# Лабораторна робота №7 — варіант 10

**functools та operator: банківські транзакції**

Студент: Мізерак Захар Володимирович, ФЕП-21.

## Запуск (Windows)

```powershell
python -m pip install -r requirements.txt
python main.py
python -m pytest -v
python -m mypy .
python -m black --check .
python -m ruff check .
```

Код предметної логіки відділено від демонстраційного запуску.

## Реалізація
Варіант 10 — успішні банківські транзакції, нормалізація, конвертація у гривню, рейтинг і reduce-агрегація. `singledispatch` підтримує JSON, CSV, Path, str, файл і список.
