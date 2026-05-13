"""
Генератор синтетических изображений строк чека.
Запуск:
    python -m model.synth_render
    python -m model.synth_render --count 3000 --output data/synthetic/generate
"""

import argparse
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = Path("data/synthetic")
DEFAULT_WORDLIST = BASE_DIR / "generate" / "wordlist.txt"
DEFAULT_OUT = BASE_DIR / "generate"
FONTS_DIR = BASE_DIR / "fonts"

IMG_HEIGHT = 48
MIN_FONT_SIZE = 22
MAX_FONT_SIZE = 34


def _load_fonts() -> list[Path]:
    fonts = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
    if not fonts:
        raise FileNotFoundError(f"Шрифты не найдены в {FONTS_DIR}")
    return fonts


def _add_noise(img: Image.Image, level: float = 0.03) -> Image.Image:
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, level * 255, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def render_line(text: str, font_paths: list[Path]) -> Image.Image:
    font_path = random.choice(font_paths)
    font_size = random.randint(MIN_FONT_SIZE, MAX_FONT_SIZE)

    try:
        font = ImageFont.truetype(str(font_path), font_size)
    except Exception:
        font = ImageFont.load_default()

    dummy = Image.new("L", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0] + 20
    text_h = bbox[3] - bbox[1] + 12

    width = max(text_w, 100)
    height = max(text_h, IMG_HEIGHT)

    bg = random.randint(245, 255)
    img = Image.new("L", (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    color = random.randint(0, 30)
    draw.text((10, 6), text, font=font, fill=color)

    if random.random() < 0.4:
        angle = random.uniform(-2.5, 2.5)
        img = img.rotate(angle, fillcolor=bg, expand=False)

    img = _add_noise(img, level=random.uniform(0.01, 0.04))

    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))

    return img


def generate(wordlist: Path, out_dir: Path, count: int) -> None:
    if not wordlist.exists():
        print(f"Файл не найден: {wordlist}")
        print("Сначала запустите: python -m model.data_generator")
        return

    lines = [l.strip() for l in wordlist.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        print("wordlist.txt пустой")
        return

    font_paths = _load_fonts()
    img_dir = out_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    gt_entries: list[str] = []
    count = min(count, len(lines)) if count <= len(lines) else count

    sample = (lines * (count // len(lines) + 1))[:count]
    random.shuffle(sample)

    for i, text in enumerate(sample):
        img = render_line(text, font_paths)
        filename = f"{i:05d}.png"
        img.save(img_dir / filename)
        gt_entries.append(f"{filename}\t{text}")

        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{count} изображений")

    gt_path = out_dir / "gt.txt"
    gt_path.write_text("\n".join(gt_entries), encoding="utf-8")

    print(f"\nГотово: {count} изображений → {img_dir}")
    print(f"Разметка: {gt_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Рендер синтетических строк чека")
    parser.add_argument("--count", type=int, default=5000)
    parser.add_argument("--wordlist", default=str(DEFAULT_WORDLIST))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    generate(Path(args.wordlist), Path(args.output), args.count)
