import chromadb
from chromadb.config import Settings
import os

# Initialize ChromaDB (local persistence)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="receipt_analysis")

def index_receipt(receipt_obj, image_hash):
    """Indexes a receipt's content for semantic search."""
    items_list = []
    for item in receipt_obj.items:
        qty = item.quantity or 1
        name = item.name or "Unknown Item"
        price = item.total_price or 0.0
        curr = item.currency or ""
        items_list.append(f"{qty}x {name} ({curr}{price})")
    
    items_text = ", ".join(items_list)
    
    store_name = receipt_obj.store_info.name or "Unknown Store"
    date = receipt_obj.receipt_info.date or "Unknown Date"
    total_val = receipt_obj.totals.total or 0.0
    total_curr = receipt_obj.totals.currency or ""

    document_content = f"""
    Store: {store_name}
    Date: {date}
    Total: {total_curr}{total_val}
    Items: {items_text}
    """
    
    collection.add(
        documents=[document_content],
        metadatas=[{"hash": image_hash, "store": store_name}],
        ids=[image_hash]
    )

def query_receipts(query_text, n_results=5):
    """Searches past receipts for relevant information."""
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results["documents"][0] if results["documents"] else []
