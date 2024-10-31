import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from alpr import scan_plate
from dotenv import load_dotenv
import requests
import datetime
import cv2
import easyocr as ocr

load_dotenv()

api_key = os.getenv('APP_KEY')

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gateless Parking - ALPR")
        self.setGeometry(100, 100, 400, 400)

        # create a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # create widgets
        self.upload_button = QPushButton("Scan plate")
        self.upload_button.clicked.connect(self.sim_ocr_prediction)
        self.layout.addWidget(self.upload_button)

        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.label = QLabel("Load an image to scan", alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: white;")

    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.gif)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaledToWidth(300))
            car = os.path.basename(file_path)
            self.label.setText(f"File: {car}")
            self.process_car_image(car)

    def process_car_image(self, car):

        try:
            plate_no = scan_plate(car)
            
            if plate_no:
                response = requests.post(
                    'http://localhost:3000/api/plate/',
                    json={
                        'plate': plate_no,
                        'address': os.getenv('LOCATION'),
                        'timestamp': datetime.datetime.now().isoformat()
                    },
                    headers={'Authorization': f'Token {api_key}'})
                
                print(response)
            else:
                self.label.setText("NOT DETECTED")
        except Exception as e:
            print(f"Error: {e}")

    def sim_prediction(self):

        # Example predictions dictionary (replace with actual values)
        predictions = {
            'x': 924.375,  # Center X-coordinate
            'y': 889.6875,  # Center Y-coordinate
            'width': 521.25,  # Width of the bounding box
            'height': 271.875  # Height of the bounding box
        }

        # Calculate bounding box coordinates
        cX = int(predictions['x'])
        cY = int(predictions['y'])
        width = int(predictions['width'])
        height = int(predictions['height'])

        half_width = int(width / 2)
        half_height = int(height / 2)

        x1 = cX - half_width
        y1 = cY - half_height
        x2 = cX + half_width
        y2 = cY + half_height

        # Load an example image (replace 'input_image.jpg' with your image)
        image = cv2.imread('honda.jpeg')

        # Draw the center point (cX, cY)
        cv2.circle(image, (cX, cY), radius=10, color=(0, 0, 255), thickness=-1)  # Red dot

        # Draw the bounding box using (x1, y1) and (x2, y2)
        cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)  # Green box

        # Add text for (cX, cY)
        cv2.putText(image, f'cX: {cX}, cY: {cY}', (cX + 10, cY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        # Add text for width and height
        #cv2.putText(image, f'Width: {width}, Height: {height}', (x1, y1 - 10),
        #            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)

        # Add text for (x1, y1) and (x2, y2)
        cv2.putText(image, f'(x1, y1): ({x1}, {y1})', (x1 - 60, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, f'(x2, y2): ({x2}, {y2})', (x2 + 10, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Display the image
        cv2.imshow('Image with Bounding Box and Annotations', image)
        cv2.waitKey(0)  # Wait until a key is pressed
        cv2.destroyAllWindows()  # Close the window

    def crop_plate(self):
                # Example predictions dictionary (replace with actual values)
        predictions = {
            'x': 924.375,  # Center X-coordinate
            'y': 889.6875,  # Center Y-coordinate
            'width': 521.25,  # Width of the bounding box
            'height': 271.875  # Height of the bounding box
        }

        # Calculate bounding box coordinates
        cX = int(predictions['x'])
        cY = int(predictions['y'])
        width = int(predictions['width'])
        height = int(predictions['height'])

        half_width = int(width / 2)
        half_height = int(height / 2)

        x1 = cX - half_width
        y1 = cY - half_height
        x2 = cX + half_width
        y2 = cY + half_height

        image = cv2.imread('honda.jpeg')

        plate_crop = image[y1:y2, x1+5:x2-5]


        return plate_crop

    def sim_ocr_prediction(self):
        reader = ocr.Reader(['en'])
        plate_crop = self.crop_plate()

        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)

        detections = reader.readtext(blur)
        im2 = plate_crop.copy()
        h, w, _ = plate_crop.shape
        mainBoxRect = h * w

        for detection in detections:

            bbox, text, _ = detection
            
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]

            print(bbox[0], bbox[1], bbox[2])
            width = abs(x1 - x2)
            height = abs(y1 - y2)

            area = width * height
            ratio = area / mainBoxRect

            #if ratio > 0.15:
            # Add text for (cX, cY)
            cv2.putText(im2, f'x1: {x1}, y1: {y1}', (x1, y1),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(im2, f'x2: {x2}, y2: {y2}', (x2, y2),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.rectangle(im2, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.imshow("ocr", im2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
            

app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())