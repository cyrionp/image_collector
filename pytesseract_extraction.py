import cv2
import pytesseract

img_raw = cv2.imread("Image_1.jpg")
#img = cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB)
text = pytesseract.image_to_string(img_raw).lower()
print(text)
