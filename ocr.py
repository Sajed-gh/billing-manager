from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='fr', use_gpu=False)


img_path = 'images/image1.jpeg'
result = ocr.ocr(img_path, cls=True)

for line in result[0]:
    print(line)
