import cv2
import os
import json
import threading
import time
from tkinter import Tk, Label, Entry, Button, Canvas
from PIL import ImageTk, Image


class CameraThread(threading.Thread):
    def __init__(self, preview_canvas, ):
        threading.Thread.__init__(self)
        self.preview_canvas = preview_canvas
        self.running = False
        self.port = 1
        self.cap = 0

    def run(self):
        self.running = True
        self.cap = cv2.VideoCapture(self.port)

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = ImageTk.PhotoImage(image)

            self.preview_canvas.create_image(0, 0, anchor='nw', image=image)
            self.preview_canvas.image = image

        self.cap.release()

    def start_capture(self):
        self.port = 0

    def stop_capture(self):
        self.port = 10
        self.cap.release()

    def stop(self):
        self.running = False

class LabelTherad(threading.Thread):
    def __init__(self, status_label):
        threading.Thread.__init__(self)
        self.status_label = status_label
        self.text = ""
        self.color = "gray"
    def start(self):
        self.status_label.config(text="Waiting to start capture", fg="gray")
        
    def update(self, text, color):
        self.status_label.config(text=text, fg=color)


def capture():

    def take_photos():
        status_thread.update("starting capture", "yellow")

        wait = 5

        # Get the user details entered in the GUI
        person_name = name_entry.get()
        person_id = generate_id()

        # Create a folder to store the person's photos if it doesn't exist
        folder_path = f"photos/{person_id}"
        os.makedirs(folder_path, exist_ok=True)

        # Capture photos of the person
        num_photos = 5  # Number of photos to capture
        photo_count = 0

        # Stop the camera thread
        camera_thread.stop_capture()
        camera_thread.stop()

        # Access the camera
        cap = cv2.VideoCapture(0)
        keep = 0

        while photo_count < num_photos:
            ret, frame = cap.read()
            if not ret:
                break

            # Face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0 and (keep % wait == 0):
                # Save the captured photo in the folder with the person's ID
                photo_filename = f"{person_id}_{photo_count+1}.jpg"
                photo_path = os.path.join(folder_path, photo_filename)
                cv2.imwrite(photo_path, frame)

                photo_count += 1
                
                keep += 1

            keep += 1

        cap.release()
        cv2.destroyAllWindows()

        # Save the person's data in a JSON file
        person_data = {
            'id': person_id,
            'name': person_name,
            'photo_count': photo_count
        }

        json_file = 'persons.json'
        persons = {}

        # Load existing person data from the JSON file if it exists
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                persons = json.load(f)

        # Append the new person's data to the existing data
        persons[person_id] = person_data

        # Save the updated person data to the JSON file
        with open(json_file, 'w') as f:
            json.dump(persons, f)

        print(f"Photos captured and saved for person with ID: {person_id}")
        status_thread.update("done with capture", "green")

        # Start the camera thread again
        # camera_thread.start_capture()
        # camera_thread.start()

    def generate_id():
        # Generate a new ID by finding the maximum ID from existing person data
        json_file = 'persons.json'

        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                persons = json.load(f)
            max_id = max(persons.keys(), key=int)
            new_id = str(int(max_id) + 1)
        else:
            new_id = "1"

        return new_id

    # Create the GUI window
    window = Tk()
    window.title("Capture Photos")
    window.geometry("450x500")

    # Create labels and entry fields for user details
    Label(window, text="Name:").pack()
    name_entry = Entry(window)
    name_entry.pack()

    # Create a canvas for the preview screen
    preview_canvas = Canvas(window, width=640, height=480)
    preview_canvas.pack()

    # Create a label to display the capturing status
    status_label = Label(window)

    status_thread = LabelTherad(status_label)
    status_thread.start()
    status_label.pack()


    # Create a button to initiate photo capture
    capture_button = Button(window, text="Capture Photos", command=take_photos)
    capture_button.pack()

    # Create the camera thread and start capturing frames
    camera_thread = CameraThread(preview_canvas)
    camera_thread.start_capture()
    camera_thread.start()

    # Run the GUI
    window.mainloop()

    # Stop the camera thread when the GUI window is closed
    camera_thread.stop_capture()
    camera_thread.stop()


if __name__ == '__main__':
    capture()
