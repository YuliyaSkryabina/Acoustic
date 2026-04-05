"""
CLI режим: python -m core.cli --input data.json --output results.json
"""
from __future__ import annotations

import argparse
import json
import sys

from .engine import calculate
from .models import CalcRequest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Акустик — расчёт уровней шума (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Пример:
  python -m core.cli --input project.json --output results.json

Формат входного JSON: объект CalcRequest с полями:
  sources  — список источников шума
  points   — список расчётных точек
  screens  — список экранов (необязательно)
  temperature, humidity — условия (необязательно)
""",
    )
    parser.add_argument("--input", "-i", required=True, help="Путь к входному JSON")
    parser.add_argument("--output", "-o", help="Путь к выходному JSON (по умолчанию stdout)")
    parser.add_argument("--pretty", action="store_true", help="Форматировать вывод")
    args = parser.parse_args()

    try:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ошибка разбора JSON: {e}", file=sys.stderr)
        sys.exit(1)

    request = CalcRequest.model_validate(data)
    response = calculate(request)

    indent = 2 if args.pretty else None
    output = response.model_dump_json(indent=indent)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Результаты сохранены в: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
