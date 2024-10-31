import easyocr as ocr
import cv2
import re

reader = ocr.Reader(['en'])
pattern = r'[^a-zA-Z0-9]'

def read_license_plate(processed_plate, plate_crop):
    detections = reader.readtext(processed_plate)

    if not detections:
        print("No plate data found")
        return None
    
    im2 = processed_plate.copy()
    h, w, _ = plate_crop.shape
    mainBoxRect = h * w
    #cv2.rectangle(im2, (0,0), (w, h), (0, 0, 255), 2)

    final = []

    for detection in detections:

        bbox, text, _ = detection
        
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]

        width = abs(x1 - x2)
        height = abs(y1 - y2)

        area = width * height
        ratio = area / mainBoxRect

        if ratio > 0.15:
            cleaned_string = re.sub(pattern, '', text)
            #cv2.rectangle(plate_crop, (x1, y1), (x2, y2), (0,255,0), 1)
            final.append(cleaned_string.upper())

    #cv2.imshow('image', plate_crop)
    return "".join(final)