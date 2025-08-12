from paddleocr import PPStructure
import cv2
import json

# Initialize parser
structure_engine = PPStructure(
    table=False,
    ocr=True,
    layout=True,
    lang='en',
    show_log=False,
)

image_path = 'images/image3.jpeg'


# Process image
result = structure_engine(image_path)

print(result)
