"""
Генератор списка строк для синтетических изображений чеков.
Запуск:
    python -m model.data_generator
    python -m model.data_generator --count 8000
"""

import argparse
import random
from pathlib import Path

BASE_DIR = Path("data/synthetic")
OUT_DIR = BASE_DIR / "generate"


def load_list(filename: str) -> list[str]:
    path = BASE_DIR / filename
    if path.exists():
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return []


_KEYWORDS = load_list("keywords.txt")
_PRODUCTS = load_list("products.txt")
_STORE_NAMES = load_list("stores.txt")


def _rand_price() -> str:
    sep = random.choice([",", "."])
    return f"{random.randint(1, 1500)}{sep}{random.randint(0, 99):02d}"


def _rand_inn() -> str:
    length = random.choice([10, 12])
    digits = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return f"ИНН {digits}"


def _apply_case(text: str) -> str:
    return text.upper() if random.random() < 0.8 else text


def generate_lines(n: int = 5000) -> list[str]:
    generators = [
        lambda: _apply_case(random.choice(_KEYWORDS)),
        lambda: _apply_case(random.choice(_STORE_NAMES)),
        lambda: f"{_apply_case(random.choice(_PRODUCTS))} {_rand_price()}",
        lambda: f"{random.uniform(0.1, 2.0):.3f} * {_rand_price()} ={_rand_price()}",
        lambda: f"ИТОГО {_rand_price()}",
        lambda: f"*** СУММА {_rand_price()} ***",
        lambda: _rand_inn(),
        lambda: f"ДАТА: {random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2020, 2026)}",
        lambda: f"НДС {random.choice(['10%', '20%'])} ={_rand_price()}",
    ]
    return [random.choice(generators)() for _ in range(n)]


def save_wordlist(count: int = 5000, filename: str = "wordlist.txt") -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / filename
    lines = generate_lines(count)
    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Сохранено {len(lines)} строк → {out_file}")
    print(f"Далее: python -m model.synth_render --count {len(lines)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация wordlist для синтетики")
    parser.add_argument("--count", type=int, default=5000)
    args = parser.parse_args()
    save_wordlist(args.count)
