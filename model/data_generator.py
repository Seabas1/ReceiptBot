"""
Генератор списка слов для trdg (TextRecognitionDataGenerator).
Создаёт синтетические изображения строк российских чеков для обучения OCR.

Запуск:
    python -m model.data_generator

    trdg -w 1 -r -l ru -c 5000 --word_split \
         --wordlist data/synthetic/wordlist.txt \
         -o data/synthetic/images
"""

import random
from pathlib import Path

_KEYWORDS = [
    "ИТОГО", "ИТОГ", "СУММА", "НДС", "ИНН", "КПП", "КАССИР",
    "МАГНИТ", "ПЯТЁРОЧКА", "ПЕРЕКРЁСТОК", "ЛЕНТА", "ДИКСИ",
    "ООО", "ИП", "АО", "КАССОВЫЙ", "ЧЕК", "ФИСКАЛЬНЫЙ",
    "Хлеб", "Молоко", "Сахар", "Масло", "Яйца", "Соль", "Вода",
    "Сок", "Чай", "Кефир", "Творог", "Рис", "Гречка", "Макароны",
]

_STORE_NAMES = [
    "ООО МАГНИТ", "ИП Петров А.В.", "АО ЛЕНТА", "ООО ПЯТЁРОЧКА",
    "ИП Сидорова М.И.", "ООО ДИКСИ", "АО ПЕРЕКРЁСТОК",
]


def _rand_price() -> str:
    return f"{random.randint(1, 999)},{random.randint(0, 99):02d}"


def _rand_date() -> str:
    return (
        f"{random.randint(1, 28):02d}."
        f"{random.randint(1, 12):02d}."
        f"{random.randint(2020, 2026)}"
    )


def _rand_inn() -> str:
    return f"ИНН {random.randint(1_000_000_000, 9_999_999_999)}"


def generate_lines(n: int = 3000) -> list[str]:
    generators = [
        lambda: random.choice(_KEYWORDS),
        lambda: f"{random.choice(_KEYWORDS)} {_rand_price()}",
        lambda: f"ИТОГО {_rand_price()}",
        lambda: _rand_inn(),
        lambda: _rand_date(),
        lambda: random.choice(_STORE_NAMES),
        lambda: f"{random.choice(_KEYWORDS)} x{random.randint(1, 5)} = {_rand_price()}",
    ]
    return [random.choice(generators)() for _ in range(n)]


def save_wordlist(path: str = "data/synthetic/wordlist.txt") -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = generate_lines()
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Сохранено {len(lines)} строк → {out}")
    print(f"\nДалее запустите trdg:")
    print(f"trdg -w 1 -r -l ru -c 5000 --word_split --wordlist {out} -o data/synthetic/images")


if __name__ == "__main__":
    save_wordlist()
