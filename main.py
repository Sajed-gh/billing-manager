import os
import json
import argparse
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

    print("[INFO] Running OCR...")
    extracted_text = extract_text(image_path)
    table = reconstruct_table(extracted_text)

    print(f"[INFO] OCR extracted {len(table)} rows.")
    for idx, row in enumerate(table):
        print(f"Row {idx}: {row}")

    print("[INFO] Running LLM reasoning...")
    receipt_obj = run(table)

    print("[INFO] Extraction complete.")
    return receipt_obj


def main():
    parser = argparse.ArgumentParser(description="Process a receipt image.")
    parser.add_argument("--image", required=True, help="Path to receipt image")
    parser.add_argument("--output", required=False, help="Output JSON file")

    args = parser.parse_args()

    receipt = process_receipt_image(args.image)

    # Save or print result
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(receipt.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved structured output to: {args.output}")
    else:
        print(json.dumps(receipt.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
