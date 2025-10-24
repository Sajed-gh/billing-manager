import numpy as np
from sklearn.cluster import DBSCAN
from PIL import Image, ImageDraw, ImageOps



def normalize_numbers(cell: str):
    try:
        val = float(cell.replace(',', '.'))
        return val
    except ValueError:
        return cell



def reconstruct_table(extracted_text, row_eps_ratio: float = 0.5):
    if not extracted_text:
        return []

    # Compute centroids of text boxes
    centroids = np.array([item['bpoly'].mean(axis=0) for item in extracted_text])
    box_heights = np.array([item['bpoly'][:, 1].max() - item['bpoly'][:, 1].min() for item in extracted_text])
    median_height = np.median(box_heights)
    eps = median_height * row_eps_ratio

    # Cluster rows using y-coordinate
    db = DBSCAN(eps=eps, min_samples=1, metric='euclidean')
    db.fit(centroids[:, 1].reshape(-1, 1))
    row_labels = db.labels_

    # Group items by row label
    rows_dict = {}
    for label, item in zip(row_labels, extracted_text):
        rows_dict.setdefault(label, []).append(item)

    # Sort each row by x-coordinate and normalize
    table = []
    for row_idx in sorted(rows_dict.keys()):
        row = rows_dict[row_idx]
        row.sort(key=lambda x: x['bpoly'][:, 0].min())
        # Normalize numbers and strip whitespace immediately
        processed_row = [normalize_numbers(cell.strip()) for cell in (cell['text'] for cell in row)]
        table.append(processed_row)

    return table



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