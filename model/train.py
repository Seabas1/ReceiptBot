"""
Дообучение модели распознавания EasyOCR (CRNN: CNN + BiLSTM + CTC)
на синтетических данных российских чеков.
Порядок действий:
  1. Сгенерировать изображения:  python -m model.data_generator
  2. Создать файл разметки:      data/synthetic/generate/gt.txt (формат: имя_файла\\tтекст)
  3. Собрать LMDB-датасет:       python -m model.train --prepare
  4. Создать копию файла LMDB    Copy-Item -Path r"data\synthetic\generate\lmdb" -Destination "data\synthetic\generate\lmdb_val" -Recurse
  4. Запустить обучение:         python -m model.train --train
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

ПАПКА_ДАННЫХ = Path("data/synthetic/generate")
ПАПКА_LMDB = ПАПКА_ДАННЫХ / "lmdb"
ПАПКА_LMDB_VAL = ПАПКА_ДАННЫХ / "lmdb_val"
ПАПКА_МОДЕЛИ = Path("model/weights")
ПАПКА_ТРЕНЕРА = Path("model/trainer")


def подготовить_lmdb() -> None:
    файл_разметки = ПАПКА_ДАННЫХ / "gt.txt"
    if not файл_разметки.exists():
        print(f"Файл разметки не найден: {файл_разметки}")
        print("    Формат строки: имя_файла.jpg\\tтекст на изображении")
        return

    ПАПКА_LMDB.mkdir(parents=True, exist_ok=True)
    команда = [
        sys.executable, str(ПАПКА_ТРЕНЕРА / "create_lmdb_dataset.py"),
        "--inputPath", str(ПАПКА_ДАННЫХ / "images"),
        "--gtFile", str(файл_разметки),
        "--outputPath", str(ПАПКА_LMDB),
    ]
    print("Создание LMDB:", " ".join(команда))
    subprocess.run(команда, check=True)


def запустить_обучение() -> None:
    ПАПКА_МОДЕЛИ.mkdir(parents=True, exist_ok=True)

    new_env = os.environ.copy()
    trainer_path = str(ПАПКА_ТРЕНЕРА.absolute())
    new_env["PYTHONPATH"] = trainer_path + os.pathsep + new_env.get("PYTHONPATH", "")

    команда = [
        sys.executable, str(ПАПКА_ТРЕНЕРА / "train.py"),
        "--train_data", str(ПАПКА_LMDB),
        "--valid_data", str(ПАПКА_LMDB_VAL),
        "--select_data", "/",
        "--batch_ratio", "1.0",
        "--Transformation", "TPS",
        "--FeatureExtraction", "ResNet",
        "--SequenceModeling", "BiLSTM",
        "--Prediction", "CTC",
        "--character", "0123456789+*/=.,!?:;()\"' *АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-",
        "--workers", "0",
        "--batch_size", "32",
        "--num_iter", "5000",
        #"--saved_model", str(ПАПКА_МОДЕЛИ / "russian_receipt.pth"),
    ]
    print("Запуск обучения:", " ".join(команда))
    subprocess.run(команда, check=True, env=new_env)


def main() -> None:
    parser = argparse.ArgumentParser(description="Дообучение EasyOCR CRNN")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true", help="Создать LMDB датасет")
    group.add_argument("--train", action="store_true", help="Запустить обучение")
    args = parser.parse_args()

    if args.prepare:
        подготовить_lmdb()
    elif args.train:
        запустить_обучение()


if __name__ == "__main__":
    main()
