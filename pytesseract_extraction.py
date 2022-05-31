import cv2
import pytesseract

img_raw = cv2.imread("Image_1.jpg")
img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
img = cv2.bilateralFilter(img_raw, 9, 75, 75)

text = pytesseract.image_to_string(img).lower()
print(text)
