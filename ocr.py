from paddleocr import PPStructure
import cv2
import json

# Initialize parser
structure_engine = PPStructure(
    table=False,
    ocr=True,
    layout=True,
    lang='en'
)

image_path = 'images/image3.jpeg'
output_image_path = 'annotated_receipt.jpg'
output_json_path = 'receipt_texts.json'

# Process image
result = structure_engine(image_path)
image = cv2.imread(image_path)

# Annotation color
color = (0, 255, 255)  # Yellow for receipt text

# Prepare JSON list
json_output = []

for item in result:
    if item['type'] != 'figure':
        continue

    for text_item in item['res']:
        text_region = text_item['text_region']  # Quadrilateral
        x_coords = [p[0] for p in text_region]
        y_coords = [p[1] for p in text_region]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        top_left = (int(x_min), int(y_min))
        bottom_right = (int(x_max), int(y_max))

        # Draw bounding box
        cv2.rectangle(image, top_left, bottom_right, color, 2)
        cv2.putText(image, text_item['text'], (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Append to JSON list
        json_output.append({
            "text": text_item['text'],
            "confidence": text_item.get('confidence', None),
            "text_region": text_region
        })

# Save annotated image
cv2.imwrite(output_image_path, image)

# Save JSON
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, ensure_ascii=False, indent=4)

print(f"Annotated receipt saved to {output_image_path}")
print(f"Text data saved to {output_json_path}")
