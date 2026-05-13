import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN: str = os.environ["TELEGRAM_TOKEN"]
EXCEL_PATH: str = os.getenv("EXCEL_PATH", "output/receipts.xlsx")
EASYOCR_MODEL_DIR: str = os.getenv("EASYOCR_MODEL_DIR", "model/weights")
