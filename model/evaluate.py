"""
Оценка точности OCR на размеченном тестовом наборе.

Метрики:
  CER (Character Error Rate) = редакционное_расстояние(pred, gt) / len(gt)
  WER (Word Error Rate)      = редакционное_расстояние(pred.split(), gt.split()) / len(gt.split())

Формат файла разметки (TSV):
  имя_изображения.jpg<TAB>ожидаемый текст

Запуск:
  python -m model.evaluate --test-dir data/real --gt data/real/gt.txt
"""

import argparse
from pathlib import Path

import editdistance

from processing.image_processor import preprocess_image
from processing.ocr_engine import run_ocr


def cer(pred: str, gt: str) -> float:
    return editdistance.eval(pred, gt) / max(len(gt), 1)


def wer(pred: str, gt: str) -> float:
    слова_pred, слова_gt = pred.split(), gt.split()
    return editdistance.eval(слова_pred, слова_gt) / max(len(слова_gt), 1)


def evaluate(test_dir: str, gt_file: str) -> None:
    gt_path = Path(gt_file)
    if not gt_path.exists():
        print(f"[!] Файл разметки не найден: {gt_file}")
        return

    пары = [
        строка.strip().split("\t", 1)
        for строка in gt_path.read_text(encoding="utf-8").splitlines()
        if "\t" in строка
    ]

    total_cer, total_wer, count = 0.0, 0.0, 0
    for имя_файла, ожидаемый in пары:
        путь = Path(test_dir) / имя_файла
        if not путь.exists():
            continue
        обработанное = preprocess_image(str(путь))
        распознанный = run_ocr(обработанное).strip()
        total_cer += cer(распознанный, ожидаемый)
        total_wer += wer(распознанный, ожидаемый)
        count += 1

    if count == 0:
        print("Нет изображений для оценки.")
        return

    print(f"Оценено образцов : {count}")
    print(f"Средний CER      : {total_cer / count:.4f}")
    print(f"Средний WER      : {total_wer / count:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-dir", default="data/real")
    parser.add_argument("--gt", default="data/real/gt.txt")
    args = parser.parse_args()
    evaluate(args.test_dir, args.gt)
