from ultralytics import YOLO #Our AI computer vision model
from PIL import Image #Python Imaging Library (Pillow) -- Allows us to manipulate an image object
import cv2 #Open Source Computer Vision Library
import os

#-------Loading in YOLOv8 nano model-----------
print("Loading YOLOv8 model......")
model = YOLO("yolov8n.pt")
print("Model loaded successfully!")

#------Load Test Image-------------
image_path = "ml/data/test_face.jpeg"

if not os.path.exists(image_path):
    print(f"Image was not found:{image_path}")
    print("Make sure you saved a face image to ml/data/test_face.jpg")
    exit()

print(f"Running detection on {image_path}.....")

#------Run detection-------------------
#results has:
#  - boxes
#  - confidence
#  - class
#  - coordinates
results = model(image_path)

#----Print Results-------------------
print("\n------Detection Results---------------------------")
for result in results:
    boxes = result.boxes
    if len(boxes) == 0:
        print("Nothing detected in this image")
    else:
        print(f"Detected {len(boxes)} object(s):")
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            print(f"-> {class_name} | confidence: {confidence:.2f} | box: ({int(x1)}, {int(y1)}, {int(x1)}, {int(y1)})")

#--------------Save annotated image-----------------
output_path = "ml/data/test_face_annotated.jpeg"
annotated = results[0].plot()
cv2.imwrite(output_path, annotated)
print(f"\nAnnotated image saved to {output_path}")
print("Open that file to see the detections!")