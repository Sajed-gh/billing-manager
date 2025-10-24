from paddleocr import PaddleOCR, PPStructure

ocr = PaddleOCR(show_log=False, lang='en')
pps = PPStructure(show_log=False, lang='en')


image_path = './images/image2.jpeg'

result1 = ocr.ocr(image_path)
result2 = pps(image_path)

print('ocr result',result1,'\n')
print('PPStructure',result2)