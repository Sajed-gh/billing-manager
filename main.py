import os
import json
from ocr_logic.ocr import extract_text
from ocr_logic.utils import reconstruct_table
from reasoning.llm_pipeline import run

def process_receipt_image(image_path):
    """
    Full end-to-end pipeline:
    1. OCR extraction
    2. Table reconstruction
    3. Structured LLM reasoning
    Returns a Pydantic Receipt object.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Step 1: OCR
    print("[INFO] Running OCR...")
    extracted_text = extract_text(image_path)
    table = reconstruct_table(extracted_text)

    print(f"[INFO] OCR extracted {len(table)} rows.")
    for idx, row in enumerate(table):
        print(f"Row {idx}: {row}")

    # Step 2: LLM reasoning
    print("[INFO] Running LLM reasoning...")
    receipt_obj = run(table)

    # Step 3: Output
    print("[INFO] Extraction complete. Structured Receipt:")
    print(json.dumps(receipt_obj.model_dump(), indent=2, ensure_ascii=False))

    return receipt_obj


if __name__ == "__main__":
    # Example image path
    image_path = "images/image1.jpeg"

    receipt = process_receipt_image(image_path)
