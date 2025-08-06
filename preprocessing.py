import cv2



img_path = 'images/image2.jpeg'

img = cv2.imread(img_path)
h,w = img.shape[:2]

max_width = 800
max_height = 600
scale = min(max_width / w, max_height / h)
new_w = int(w * scale)
new_h = int(h * scale)

img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(img_gray, (3, 3), 0)

theshold = cv2.adaptiveThreshold(
    blurred, 
    255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv2.THRESH_BINARY_INV, 
    31, 
    10)


cv2.imshow('Grayscale Image', blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('images/image2_processed.jpeg', theshold)