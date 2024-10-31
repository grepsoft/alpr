import cv2
import os
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from util import read_license_plate

load_dotenv()

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

def scan_plate(car):
    print("Extracting plate....")
    result = CLIENT.infer(car, model_id="licence-plate-dausq/2")

    if not result:
        return None
    
    predictions = result['predictions'][0]

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

    image = cv2.imread(car)

    plate_crop = image[y1:y2, x1+5:x2-5]

    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5,5), 0)

    plate_text = read_license_plate(blur, plate_crop)

    return plate_text