from paddleocr import PaddleOCR
import os
import numpy as np
from PIL import Image
from ocr_logic.utils import reconstruct_table, draw_bpolys


ocr_engine = PaddleOCR(show_log=False, lang="en",use_gpu=False)

def extract_text(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f'Image not found: {image_path}')

    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)

    # Call OCR engine
    result = ocr_engine.ocr(image_np)

    texts = []
    for line in result[0]:
        box, (text, conf) = line
        if conf < 0.6 or not text.strip():
            continue
        texts.append({
            "text": text.strip(),
            "bpoly": np.array(box)
        })
    return texts

if __name__ == '__main__':
    image_path = "images/image3.jpeg"
    extracted_text = extract_text(image_path)
    table = reconstruct_table(extracted_text)

    print("Extracted Table:")
    for r_idx, row in enumerate(table):
        print(f"Row {r_idx}: {row}")

    # Draw bpoly for visualization
    image_with_bpoly = draw_bpolys(image_path, extracted_text)
    image_with_bpoly.show()
