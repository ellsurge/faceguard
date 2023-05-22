# main.py

import capture_photos
import train_model
import face_recognition

# Step 1: Capture Photos
capture_photos.capture()

# Step 2: Train Model
train_model.train()

# Step 3: Face Recognition
face_recognition.recognize()
