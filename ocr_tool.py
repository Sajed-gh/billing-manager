from paddleocr import PPStructure
import cv2
import numpy as np


structure_engine = PPStructure(show_log=False, lang='en')

image_path = 'images/image7.jpg'

result = structure_engine(image_path)
doc_bbox = result[0].get('bbox',[])

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
        
if doc_bbox:
    doc_height = doc_bbox[3] - doc_bbox[1]
    y_threshold = int(0.01 * doc_height)  # 1% of document height
else:
    y_threshold = 10

    
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

    if y_min < 0.25 * doc_height:
        zone = 'header'
    elif y_min < 0.75 * doc_height:
        zone = 'body'
    else:
        zone = 'footer'

    final_output.append({
        'text': merged_text,
        'box': merged_box,
        'zone': zone
    })

for line in final_output:
    print(line)



