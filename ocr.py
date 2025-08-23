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

for item in result:
    entry = {'type': item['type'], 'res': []}
    for text_item in item.get('res', []):
        text_region = text_item.get('text_region')
        if not text_region:
            continue

        x_coords = [p[0] for p in text_region]
        y_coords = [p[1] for p in text_region]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        top_left = (int(x_min), int(y_min))
        bottom_right = (int(x_max), int(y_max))

        cv2.polylines(image, [np.array(text_region, dtype=np.int32)], True, box_color, 3)
        
        text_pos = (top_left[0], max(top_left[1] - 10, 10))
        cv2.putText(image, text_item.get('text', ''), text_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        entry['res'].append({
            "text": text_item.get('text', ''),
            "confidence": text_item.get('confidence', 0),
            "text_region": text_region,
            "box": [top_left, bottom_right]
        })

    json_output.append(entry)

cv2.imwrite(output_image_path, image)

with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, ensure_ascii=False, indent=4)

print(f"Annotated receipt saved to {output_image_path}")
print(f"Text data saved to {output_json_path}")
