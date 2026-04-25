import os
import json
import argparse
import hashlib
from reasoning.llm_pipeline import run_multimodal
from database import get_receipt_by_hash


def calculate_hash(image_path):
    """Generates a SHA-256 hash for a file."""
    sha256_hash = hashlib.sha256()
    with open(image_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_receipt_image(image_path, use_cache=True):
    """
    Directly uses Gemini's Multimodal capabilities to extract structured data.
    Includes a caching layer to avoid redundant LLM calls.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img_hash = calculate_hash(image_path)
    
    if use_cache:
        cached_receipt = get_receipt_by_hash(img_hash)
        if cached_receipt:
            print("[INFO] Found cached analysis in database.")
            return cached_receipt.raw_json, img_hash

    print("[INFO] Running Multimodal LLM reasoning (Vision)...")
    receipt_obj = run_multimodal(image_path)

    print("[INFO] Extraction complete.")
    return receipt_obj, img_hash


def main():
    parser = argparse.ArgumentParser(description="Process a receipt image using Vision LLM.")
    parser.add_argument("--image", required=True, help="Path to receipt image")
    parser.add_argument("--output", required=False, help="Output JSON file")
    parser.add_argument("--no-cache", action="store_true", help="Disable database caching")

    args = parser.parse_args()

    try:
        # main.py returns a tuple (data, hash)
        receipt_data, _ = process_receipt_image(args.image, use_cache=not args.no_cache)
        
        # Handle if it came from cache (dict) or LLM (Pydantic)
        output_data = receipt_data if isinstance(receipt_data, dict) else receipt_data.model_dump()

        # Save or print result
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Saved structured output to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
