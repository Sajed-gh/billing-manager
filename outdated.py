from paddleocr import PPStructure
import cv2
import json
import numpy as np

# Initialize parser
structure_engine = PPStructure(show_log=False)

image_path = 'images/image1.jpeg'
output_image_path = 'output/annotated_receipt.jpg'
output_json_path = 'output/receipt_texts.json'

# Process image
result = structure_engine(image_path)
image = cv2.imread(image_path)

box_color = (0, 255, 0)  # Green box
text_color = (0, 0, 255)  # Red text

json_output = []

# Step 1: Collect all boxes from result
all_boxes = []
for item in result:
    for text_item in item.get('res', []):
        text_region = text_item.get('text_region')
        if not text_region:
            continue
        x_coords = [p[0] for p in text_region]
        y_coords = [p[1] for p in text_region]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        all_boxes.append({
            "text": text_item.get('text', ''),
            "confidence": text_item.get('confidence', 0),
            "text_region": text_item.get('text_region'),
            "box": [(int(x_min), int(y_min)), (int(x_max), int(y_max))]
        })

# Step 2: Merge boxes into lines based on y-coordinate
y_threshold = 30
all_boxes.sort(key=lambda b: b['box'][0][1])  # sort by y_min

lines = []
for box in all_boxes:
    placed = False
    for line in lines:
        # If box is vertically close to existing line
        line_y_avg = np.mean([b['box'][0][1] for b in line['boxes']])
        if abs(box['box'][0][1] - line_y_avg) <= y_threshold:
            line['boxes'].append(box)
            placed = True
            break
    if not placed:
        lines.append({"boxes": [box]})

# Step 3: Sort each line horizontally and merge bounding boxes
for line in lines:
    line['boxes'].sort(key=lambda b: b['box'][0][0])  # sort by x_min
    merged_text = " ".join([b['text'] for b in line['boxes']])
    
    # Compute merged bounding box
    x_min = min(b['box'][0][0] for b in line['boxes'])
    y_min = min(b['box'][0][1] for b in line['boxes'])
    x_max = max(b['box'][1][0] for b in line['boxes'])
    y_max = max(b['box'][1][1] for b in line['boxes'])
    merged_box = [(x_min, y_min), (x_max, y_max)]

    # Draw merged bounding box
    cv2.rectangle(image, merged_box[0], merged_box[1], box_color, 2)
    # Draw merged text above box
    text_pos = (merged_box[0][0], max(merged_box[0][1] - 10, 10))
    cv2.putText(image, merged_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

    # Save merged line to JSON
    json_output.append({
        "merged_text": merged_text,
        "merged_box": merged_box,
        "res": line['boxes']
    })

# Step 4: Save outputs
cv2.imwrite(output_image_path, image)
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, ensure_ascii=False, indent=4)

print(f"Annotated receipt saved to {output_image_path}")
print(f"Text data saved to {output_json_path}")



