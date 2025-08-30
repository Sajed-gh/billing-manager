from paddleocr import PPStructure
import cv2
import numpy as np


structure_engine = PPStructure(show_log=False, lang='en')

image_path = 'images/image4.jpeg'

result = structure_engine(image_path)
image = cv2.imread(image_path)

output = []
for item in result:
    for element in item.get('res',[]):
        region = element.get('text_region')
        if not region:
            continue
        x_coords = [p[0] for p in region]
        y_coords = [p[1] for p in region]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        output.append({
            'text': element.get('text',''),
            'confidence': element.get('confidence',0),
            'box': [(x_min,y_min),(x_max,y_max)]
        })
        
y_threshold = 30
output.sort(key=lambda b: b['box'][0][1])
lines= []
for box in output:
    placed = False
    for line in lines: 
        line_ref = np.mean([b['box'][0][1] for b in line['boxes']])
        if abs(box['box'][0][1] - line_ref) <= y_threshold:
            line['boxes'].append(box)
            placed= True
            break
    if not placed: 
        lines.append({"boxes": [box]})

final_output = []               
for line in lines:
    line['boxes'].sort(key=lambda b:b['box'][0][0])
    merged_text = " ".join([b['text'] for b in line['boxes']])

    x_min = min(b['box'][0][0] for b in line['boxes'])
    y_min = min(b['box'][0][1] for b in line['boxes'])
    x_max = max(b['box'][1][0] for b in line['boxes'])
    y_max = max(b['box'][1][1] for b in line['boxes'])
    merged_box = [(x_min,y_min),(x_max,y_max)]

    final_output.append({
        'merged_text': merged_text,
        'merged_box': merged_box
    })

print(final_output)



# result = [{ 
#     'type': text,
#     "bbox": [n1,n2,n3,n4], 'img': array([[]]),
#     'res': [{'text': text, 'confidence': real,"text_region": [[],[],[],[]]},...{}]
# }]


