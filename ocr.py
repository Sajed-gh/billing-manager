from paddleocr import PPStructure
import os
import numpy as np
from sklearn.cluster import DBSCAN
from PIL import Image, ImageDraw, ImageOps

ocr_engine = PPStructure(show_log=False, lang="en",use_gpu=False)


# -----------------------------
# Extract text with bounding polygons
# -----------------------------
def extract_text(image_path: str):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f'Image not found: {image_path}')

    # Load image, convert to RGB
    from PIL import Image
    import numpy as np

    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)

    # Call OCR engine
    result = ocr_engine(image_np)

    extracted_text = []
    for element in result[0].get('res', []):
        bpoly = element.get('text_region')
        if not bpoly:
            continue
        extracted_text.append({
            "text": element.get('text', '').strip(),
            "bpoly": np.array(bpoly)
        })
    return extracted_text


# -----------------------------
# Reconstruct table
# -----------------------------
def reconstruct_table(extracted_text, row_eps_ratio: float = 0.5):
    if not extracted_text:
        return []

    # Compute centroids of text boxes
    centroids = np.array([item['bpoly'].mean(axis=0) for item in extracted_text])

    # Calculate eps relative to median y-coordinate distance
    box_heights = np.array([item['bpoly'][:, 1].max() - item['bpoly'][:, 1].min() for item in extracted_text])
    median_height = np.median(box_heights)
    eps = median_height * row_eps_ratio

    # Cluster rows
    db = DBSCAN(eps=eps, min_samples=1, metric='euclidean')
    db.fit(centroids[:, 1].reshape(-1, 1))
    row_labels = db.labels_

    # Group items by row label
    rows_dict = {}
    for label, item in zip(row_labels, extracted_text):
        rows_dict.setdefault(label, []).append(item)

    # Sort each row by leftmost x-coordinate
    table = []
    for row_idx in sorted(rows_dict.keys()):
        row = rows_dict[row_idx]
        row.sort(key=lambda x: x['bpoly'][:, 0].min())
        table.append([cell['text'] for cell in row])

    return table

# -----------------------------
# Draw bounding polygons on image
# -----------------------------
def draw_bpolys(image_path, extracted_text):
    """
    Draw bounding polygons (bpolys) on the image.
    Returns a PIL Image.
    """
    image = Image.open(image_path)
    # Correct orientation before drawing
    image = ImageOps.exif_transpose(image)
    draw = ImageDraw.Draw(image)

    for item in extracted_text:
        bpoly = item['bpoly']  # np.array([[x1,y1],[x2,y2],...])
        coords = [tuple(pt) for pt in bpoly]
        coords.append(tuple(bpoly[0]))  # close the polygon
        draw.line(coords, fill="green", width=8)

    return image

# -----------------------------
# Main test
# -----------------------------
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
