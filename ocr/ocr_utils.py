import logging
import threading
from PIL import Image
import numpy as np
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

class OCRTimeoutError(Exception):
    pass

def _read_text_worker(img_np, result_holder):
    try:
        result_holder.append(reader.readtext(img_np))
    except Exception as e:
        logging.error(f"OCR internal failure: {e}")

def extract_text_from_image(path: str, timeout: int = 15) -> list:
    logging.info(f"Loading image: {path}")

    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((img.width // 2, img.height // 2))  # speed up OCR
        img_np = np.array(img)

        logging.info(f"Running OCR on: {path}")
        result_holder = []
        thread = threading.Thread(target=_read_text_worker, args=(img_np, result_holder))
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            logging.warning(f"OCR timed out on: {path}")
            raise OCRTimeoutError(f"OCR timed out on {path}")

        result = [res[1] for res in result_holder[0]] if result_holder else []
        logging.info(f"OCR result for {path}: {result}")
        return result

    except Exception as e:
        logging.error(f"OCR failed on file: {path} with error: {e}")
        return []
