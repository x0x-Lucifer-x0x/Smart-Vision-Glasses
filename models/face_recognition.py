# import threading
# import cv2
# import face_recognition
# import os
# import time
# import pyttsx3
# import numpy as np
# from queue import Queue

# # Path for saving the dataset
# DATASET_PATH = 'src\\dataset\\images'

# # Ensure the dataset directory exists
# if not os.path.exists(DATASET_PATH):
#     os.makedirs(DATASET_PATH)

# # Initialize TTS engine and queue
# engine = pyttsx3.init()
# tts_queue = Queue()

# # Function to handle text-to-speech requests safely with a dedicated thread
# def tts_worker():
#     """TTS worker that speaks messages sequentially from the queue."""
#     while True:
#         text = tts_queue.get()  # Wait for new text to process
#         if text is None:  # Sentinel value to stop the thread
#             break
#         engine.say(text)
#         engine.runAndWait()
#         tts_queue.task_done()

# # Start the TTS worker thread
# tts_thread = threading.Thread(target=tts_worker, daemon=True)
# tts_thread.start()

# def speak(text):
#     """Add text to the TTS queue for the worker to process."""
#     tts_queue.put(text)

# # Load known faces from the dataset
# known_face_encodings = []
# known_face_names = []

# def load_known_faces():
#     """Function to load or reload known faces and names from the dataset."""
#     global known_face_encodings, known_face_names
#     known_face_encodings = []
#     known_face_names = []

#     for filename in os.listdir(DATASET_PATH):
#         if filename.endswith(".jpg"):
#             img_path = os.path.join(DATASET_PATH, filename)
#             image = face_recognition.load_image_file(img_path)

#             encodings = face_recognition.face_encodings(image)
#             if len(encodings) > 0:
#                 known_face_encodings.append(encodings[0])
#                 known_face_names.append(os.path.splitext(filename)[0])
#             else:
#                 print(f"No face found in {filename}, skipping.")

# # Load known faces at the start
# load_known_faces()

# # Initialize video capture
# video_capture = cv2.VideoCapture(1)

# # Function to take a photo with a 5-second countdown and voice prompts
# def take_photo():
#     for i in range(5, 0, -1):
#         speak(f"{i}")
#         time.sleep(1)

#     ret, frame = video_capture.read()
#     if not ret:
#         speak("Failed to capture an image.")
#         return

#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(rgb_frame)

#     if len(face_locations) == 0:
#         speak("No face detected in the photo.")
#         return

#     for (top, right, bottom, left) in face_locations:
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#     speak("Please enter the name of the person.")
#     name = input("Please enter the name of the person: ").strip()

#     speak(f"You entered {name}. Please confirm by typing 'yes' or 'no'.")
#     confirmation = input(f"You entered '{name}'. Please confirm by typing 'yes' or 'no': ").strip().lower()

#     if confirmation == "yes":
#         img_path = os.path.join(DATASET_PATH, f'{name}.jpg')
#         cv2.imwrite(img_path, frame)
#         speak(f"Photo of {name} saved successfully!")

#         load_known_faces()  # Reload known faces after saving a new photo
#     else:
#         speak("Name not confirmed. Photo not saved.")

# # Function to start face recognition in real-time video
# def start_face_recognition():
#     greeted_people = set()

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Failed to capture frame.")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             name = "Unknown"

#             if known_face_encodings:
#                 face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
#                 if face_distances.size > 0:
#                     best_match_index = np.argmin(face_distances)
#                     if face_distances[best_match_index] < 0.6:
#                         name = known_face_names[best_match_index]
#                         if name not in greeted_people:
#                             speak(f"{name} is in front of you.")
#                             greeted_people.add(name)

#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

#         cv2.imshow('Video', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     video_capture.release()
#     cv2.destroyAllWindows()

# # Run face recognition in a separate thread
# face_recognition_thread = threading.Thread(target=start_face_recognition, daemon=True)
# face_recognition_thread.start()

# # Cleanup: Send stop signal to the TTS thread when done
# def cleanup():
#     tts_queue.put(None)
#     tts_thread.join()

# # Make sure to call `cleanup()` before the program exits to stop the TTS thread.


# v - 0.2 #################################################################################################################################
import threading
import cv2
import face_recognition
import os
import time
import pyttsx3
import numpy as np
from queue import Queue

# Path for saving the dataset
DATASET_PATH = 'src\\dataset\\images'

# Ensure the dataset directory exists
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

# Initialize TTS engine and queue
engine = pyttsx3.init()
tts_queue = Queue()

# Function to handle text-to-speech requests safely with a dedicated thread
def tts_worker():
    """TTS worker that speaks messages sequentially from the queue."""
    while True:
        text = tts_queue.get()  # Wait for new text to process
        if text is None:  # Sentinel value to stop the thread
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

# Start the TTS worker thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    """Add text to the TTS queue for the worker to process."""
    tts_queue.put(text)

# Load known faces from the dataset
known_face_encodings = []
known_face_names = []

def load_known_faces():
    """Function to load or reload known faces and names from the dataset."""
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(DATASET_PATH):
        if filename.endswith(".jpg"):
            img_path = os.path.join(DATASET_PATH, filename)
            image = face_recognition.load_image_file(img_path)

            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])
            else:
                print(f"No face found in {filename}, skipping.")

# Load known faces at the start
load_known_faces()

# Initialize video capture
video_capture = cv2.VideoCapture(1)

def take_photo():
    while True:
        # Capture a frame to check for a person
        ret, frame = video_capture.read()
        if not ret:
            speak("Failed to capture an image.")
            return

        # Convert the captured image to RGB format for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Check if any face is detected in the frame
        if len(face_locations) == 0:
            # No face detected, inform the user and keep checking
            speak("No person detected in the frame.")
            time.sleep(2)  # Wait a short period before checking again
            continue

        # If a face is detected, check if the person is known or unknown
        person_found = False
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                # Known person detected
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                speak(f"{name} is already known. Returning to the main menu.")
                person_found = True
                break  # Exit loop as a known person was detected

        if person_found:
            # Close the capture window and return to main menu
            cv2.destroyAllWindows()
            return  # Exit `take_photo`, returning control to `main.py`

        # If no known person is found, proceed with photo capture
        speak("Unknown person detected. Starting the photo process in 5 seconds.")
        
        # Start countdown with a warning for unknown person
        for i in range(8, 0, -1):
            speak(f"{i}")
            print(i)
            time.sleep(1)

        # Capture the frame after the countdown
        ret, frame = video_capture.read()
        if not ret:
            speak("Failed to capture an image.")
            return

        # Convert the captured image to RGB format and recheck for faces
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        # If no face is detected in the captured image, notify the user and exit
        if len(face_locations) == 0:
            speak("No face detected in the photo. Returning to main menu.")
            return

        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Take name input using text
        speak("Please enter the name of the person.")
        name = input("Please enter the name of the person: ").strip()

        # Ask for confirmation using text
        speak(f"You entered {name}. Please confirm by typing 'yes' or 'no'.")
        confirmation = input(f"You entered '{name}'. Please confirm by typing 'yes' or 'no': ").strip().lower()

        if confirmation == "yes":
            img_path = os.path.join(DATASET_PATH, f'{name}.jpg')
            cv2.imwrite(img_path, frame)
            speak(f"Photo of {name} taken and saved successfully!")
            
            # Reload known faces after saving a new photo
            load_known_faces()

            # Now check if the person is recognized in the frame after adding to known faces
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                # Draw updated name on the frame
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            
            # Display the frame briefly with the updated label
            cv2.imshow('Updated Photo', frame)
            cv2.waitKey(2000)  # Display for 2 seconds
            cv2.destroyWindow('Updated Photo')
        else:
            speak("Name not confirmed. Photo not saved.")

        # Close capture window and return to main menu after photo process is complete
        cv2.destroyAllWindows()
        return  # Exit `take_photo`, returning control to `main.py`





# Function to start face recognition in real-time video
def start_face_recognition():
    greeted_people = set()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"

            if known_face_encodings:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                if face_distances.size > 0:
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.6:
                        name = known_face_names[best_match_index]
                        if name not in greeted_people:
                            speak(f"{name} is in front of you.")
                            greeted_people.add(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Run face recognition in a separate thread
face_recognition_thread = threading.Thread(target=start_face_recognition, daemon=True)
face_recognition_thread.start()



# Cleanup: Send stop signal to the TTS thread when done
def cleanup():
    tts_queue.put(None)
    tts_thread.join()

# Make sure to call `cleanup()` before the program exits to stop the TTS thread.


# v - 0.3 ###########################################################################################################################

# import threading
# import cv2
# import face_recognition
# import os
# import time
# import pyttsx3
# import numpy as np
# from queue import Queue
# from datetime import datetime

# # Constants
# DATASET_PATH = 'src\\dataset\\images'
# CONFIDENCE_THRESHOLD = 0.6
# FRAME_CHECK_DELAY = 2
# COUNTDOWN_TIME = 5

# # Ensure the dataset directory exists
# if not os.path.exists(DATASET_PATH):
#     os.makedirs(DATASET_PATH)

# class FaceRecognitionSystem:
#     def __init__(self):
#         self.known_face_encodings = []
#         self.known_face_names = []
#         self.video_capture = cv2.VideoCapture(1)
#         self.tts_queue = Queue()
#         self.engine = pyttsx3.init()
#         self.last_greeting_time = {}  # Track when each person was last greeted
#         self.greeting_cooldown = 60  # Seconds before greeting the same person again
        
#         # Start TTS thread
#         self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
#         self.tts_thread.start()
        
#         # Load known faces
#         self.load_known_faces()

#     def _tts_worker(self):
#         """Enhanced TTS worker with priority handling."""
#         while True:
#             text = self.tts_queue.get()
#             if text is None:
#                 break
#             self.engine.say(text)
#             self.engine.runAndWait()
#             self.tts_queue.task_done()

#     def speak(self, text, priority=False):
#         """Speak text with optional priority."""
#         if priority:
#             # Clear queue for priority messages
#             while not self.tts_queue.empty():
#                 try:
#                     self.tts_queue.get_nowait()
#                 except Queue.Empty:
#                     break
#         self.tts_queue.put(text)

#     def load_known_faces(self):
#         """Load known faces with error handling and status updates."""
#         self.known_face_encodings = []
#         self.known_face_names = []
        
#         if not os.listdir(DATASET_PATH):
#             self.speak("No known faces in database. Please add some faces first.")
#             return

#         self.speak("Loading known faces...")
#         for filename in os.listdir(DATASET_PATH):
#             if filename.endswith(".jpg"):
#                 try:
#                     img_path = os.path.join(DATASET_PATH, filename)
#                     image = face_recognition.load_image_file(img_path)
#                     encodings = face_recognition.face_encodings(image)
                    
#                     if encodings:
#                         self.known_face_encodings.append(encodings[0])
#                         name = os.path.splitext(filename)[0]
#                         self.known_face_names.append(name)
#                     else:
#                         self.speak(f"Warning: No face found in {filename}")
#                 except Exception as e:
#                     self.speak(f"Error loading {filename}: {str(e)}")

#         self.speak(f"Loaded {len(self.known_face_names)} faces successfully.")

#     def check_frame_for_faces(self, frame):
#         """Check frame for faces and return face data."""
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#         return face_locations, face_encodings

#     def identify_person(self, face_encoding):
#         """Identify a person from their face encoding."""
#         if not self.known_face_encodings:
#             return "Unknown", 1.0

#         face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
#         best_match_index = np.argmin(face_distances)
        
#         if face_distances[best_match_index] < CONFIDENCE_THRESHOLD:
#             return self.known_face_names[best_match_index], face_distances[best_match_index]
#         return "Unknown", face_distances[best_match_index]

#     def take_photo(self):
#         """Enhanced photo capture process with smart detection and interaction."""
#         self.speak("Starting smart face detection mode...")
        
#         while True:
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Camera error. Please check the connection.", priority=True)
#                 return False

#             face_locations, face_encodings = self.check_frame_for_faces(frame)

#             if not face_locations:
#                 self.speak("No person detected in frame. Please position yourself in front of the camera.")
#                 time.sleep(FRAME_CHECK_DELAY)
#                 continue

#             # Check if detected person is already known
#             for face_encoding in face_encodings:
#                 name, confidence = self.identify_person(face_encoding)
                
#                 if name != "Unknown":
#                     self.speak(f"{name} is already in the database. No need to take a new photo.", priority=True)
#                     return False

#             # Unknown person detected - proceed with photo capture
#             self.speak("New person detected. Starting photo capture process...")
            
#             # Position guidance
#             face_center = ((face_locations[0][1] + face_locations[0][3]) // 2,
#                           (face_locations[0][0] + face_locations[0][2]) // 2)
#             frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
            
#             # Guide person to center of frame
#             if abs(face_center[0] - frame_center[0]) > 50:
#                 if face_center[0] < frame_center[0]:
#                     self.speak("Please move slightly to your right.")
#                 else:
#                     self.speak("Please move slightly to your left.")
#                 time.sleep(1)
#                 continue
                
#             # Countdown
#             self.speak("Position good! Starting countdown in:")
#             for i in range(COUNTDOWN_TIME, 0, -1):
#                 self.speak(str(i))
#                 time.sleep(1)

#             # Capture final image
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Failed to capture image.", priority=True)
#                 return False

#             # Get person's name
#             self.speak("Please enter the person's name.")
#             name = input("Enter name: ").strip()
            
#             # Confirmation
#             self.speak(f"You entered {name}. Please confirm by typing 'yes' or 'no'.")
#             if input(f"Confirm name '{name}' (yes/no): ").lower() != 'yes':
#                 self.speak("Photo capture cancelled.")
#                 return False

#             # Save photo
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"{name}_{timestamp}.jpg"
#             img_path = os.path.join(DATASET_PATH, filename)
#             cv2.imwrite(img_path, frame)
            
#             self.speak(f"Photo of {name} saved successfully!")
#             self.load_known_faces()  # Reload known faces
#             return True

#     def start_face_recognition(self):
#         """Real-time face recognition with enhanced features."""
#         self.speak("Starting real-time face recognition...")
        
#         while True:
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Camera error detected.", priority=True)
#                 break

#             face_locations, face_encodings = self.check_frame_for_faces(frame)

#             current_time = time.time()
            
#             for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                 name, confidence = self.identify_person(face_encoding)
                
#                 # Calculate rough distance based on face box size
#                 face_size = bottom - top
#                 estimated_distance = round((1000 / face_size) * 0.3, 1)  # Rough estimation in meters

#                 # Draw face box and info
#                 color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
#                 cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
#                 # Add info text
#                 info_text = f"{name} ({confidence:.2f})"
#                 cv2.putText(frame, info_text, (left, top - 10), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#                 cv2.putText(frame, f"{estimated_distance}m", (left, bottom + 20),
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#                 # Speak updates with cooldown
#                 if name != "Unknown":
#                     if name not in self.last_greeting_time or \
#                        current_time - self.last_greeting_time[name] > self.greeting_cooldown:
#                         self.speak(f"{name} is {estimated_distance} meters in front of you.")
#                         self.last_greeting_time[name] = current_time
#                 else:
#                     # For unknown faces, trigger photo capture process
#                     self.speak("Unknown person detected. Would you like to add them?")
#                     if input("Add unknown person? (yes/no): ").lower() == 'yes':
#                         if self.take_photo():
#                             break  # Return to main menu after successful photo capture

#             cv2.imshow('Face Recognition', frame)
            
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.video_capture.release()
#         cv2.destroyAllWindows()

#     def cleanup(self):
#         """Cleanup resources."""
#         self.tts_queue.put(None)
#         self.tts_thread.join()
#         self.video_capture.release()
#         cv2.destroyAllWindows()

# # Usage example:
# if __name__ == "__main__":
#     system = FaceRecognitionSystem()
#     try:
#         # You can call either take_photo() or start_face_recognition()
#         system.start_face_recognition()
#     finally:
#         system.cleanup()


# v - 0.4 ###############################################################################################################################
# import threading
# import cv2
# import face_recognition
# import os
# import time
# import pyttsx3
# import numpy as np
# from queue import Queue
# from datetime import datetime

# # Constants
# DATASET_PATH = 'src\\dataset\\images'
# CONFIDENCE_THRESHOLD = 0.6
# FRAME_CHECK_DELAY = 2
# COUNTDOWN_TIME = 5

# # Ensure the dataset directory exists
# if not os.path.exists(DATASET_PATH):
#     os.makedirs(DATASET_PATH)

# class FaceRecognitionSystem:
#     def __init__(self):
#         self.known_face_encodings = []
#         self.known_face_names = []
#         self.video_capture = cv2.VideoCapture(0)
#         self.tts_queue = Queue()
#         self.engine = pyttsx3.init()
#         self.last_greeting_time = {}  # Track when each person was last greeted
#         self.greeting_cooldown = 60  # Seconds before greeting the same person again
        
#         # Start TTS thread
#         self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
#         self.tts_thread.start()
        
#         # Load known faces
#         self.load_known_faces()

#     def _tts_worker(self):
#         """Enhanced TTS worker with priority handling."""
#         while True:
#             text = self.tts_queue.get()
#             if text is None:
#                 break
#             try:
#                 self.engine.say(text)
#                 self.engine.runAndWait()
#             except RuntimeError as e:
#                 if "run loop already started" in str(e):
#                     # The run loop has already started, so we need to wait for it to finish
#                     self.engine.endLoop()
#                     self.engine.say(text)
#                     self.engine.runAndWait()
#                 else:
#                     # Handle other exceptions
#                     self.speak(f"TTS error: {str(e)}", priority=True)
#             self.tts_queue.task_done()

#     def speak(self, text, priority=False):
#         """Speak text with optional priority."""
#         if priority:
#             # Clear queue for priority messages
#             while not self.tts_queue.empty():
#                 try:
#                     self.tts_queue.get_nowait()
#                 except Queue.Empty:
#                     break
#         self.tts_queue.put(text)

#     def load_known_faces(self):
#         """Load known faces with error handling and status updates."""
#         self.known_face_encodings = []
#         self.known_face_names = []
        
#         if not os.listdir(DATASET_PATH):
#             self.speak("No known faces in database. Please add some faces first.")
#             return

#         self.speak("Loading known faces...")
#         for filename in os.listdir(DATASET_PATH):
#             if filename.endswith(".jpg"):
#                 try:
#                     img_path = os.path.join(DATASET_PATH, filename)
#                     image = face_recognition.load_image_file(img_path)
#                     encodings = face_recognition.face_encodings(image)
                    
#                     if encodings:
#                         self.known_face_encodings.append(encodings[0])
#                         name = os.path.splitext(filename)[0]
#                         self.known_face_names.append(name)
#                     else:
#                         self.speak(f"Warning: No face found in {filename}")
#                 except Exception as e:
#                     self.speak(f"Error loading {filename}: {str(e)}")

#         self.speak(f"Loaded {len(self.known_face_names)} faces successfully.")

#     def check_frame_for_faces(self, frame):
#         """Check frame for faces and return face data."""
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#         return face_locations, face_encodings

#     def identify_person(self, face_encoding):
#         """Identify a person from their face encoding."""
#         if not self.known_face_encodings:
#             return "Unknown", 1.0

#         face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
#         best_match_index = np.argmin(face_distances)
        
#         if face_distances[best_match_index] < CONFIDENCE_THRESHOLD:
#             return self.known_face_names[best_match_index], face_distances[best_match_index]
#         return "Unknown", face_distances[best_match_index]

#     def take_photo(self):
#         """Enhanced photo capture process with smart detection and interaction."""
#         self.speak("Starting smart face detection mode...")
    
#         while True:
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Camera error. Please check the connection.", priority=True)
#                 return False

#             face_locations, face_encodings = self.check_frame_for_faces(frame)

#             if not face_locations:
#                 self.speak("No person detected in frame. Please position yourself in front of the camera.")
#                 time.sleep(FRAME_CHECK_DELAY)
#                 continue

#             # Unknown person detected - proceed with photo capture
#             self.speak("New person detected. Starting photo capture process...")
            
#             # Position guidance
#             face_center = ((face_locations[0][1] + face_locations[0][3]) // 2,
#                         (face_locations[0][0] + face_locations[0][2]) // 2)
#             frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
            
#             # Guide person to center of frame
#             if abs(face_center[0] - frame_center[0]) > 50:
#                 if face_center[0] < frame_center[0]:
#                     self.speak("Please move slightly to your right.")
#                 else:
#                     self.speak("Please move slightly to your left.")
#                 time.sleep(1)
#                 continue
                
#             # Countdown
#             self.speak("Position good! Starting countdown in:")
#             for i in range(COUNTDOWN_TIME, 0, -1):
#                 self.speak(str(i))
#                 time.sleep(1)

#             # Capture final image
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Failed to capture image.", priority=True)
#                 return False

#             # Get person's name
#             self.speak("Please enter the person's name.")
#             name = input("Enter name: ").strip()
            
#             # Confirmation
#             self.speak(f"You entered {name}. Please confirm by typing 'yes' or 'no'.")
#             if input(f"Confirm name '{name}' (yes/no): ").lower() != 'yes':
#                 self.speak("Photo capture cancelled.")
#                 return False

#             # Save photo
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"{name}_{timestamp}.jpg"
#             img_path = os.path.join(DATASET_PATH, filename)
#             cv2.imwrite(img_path, frame)
            
#             self.speak(f"Photo of {name} saved successfully!")
#             self.load_known_faces()  # Reload known faces
#             return True

#     def start_face_recognition(self):
#         """Real-time face recognition with enhanced features."""
#         self.speak("Starting real-time face recognition...")
        
#         while True:
#             ret, frame = self.video_capture.read()
#             if not ret:
#                 self.speak("Camera error detected.", priority=True)
#                 break

#             face_locations, face_encodings = self.check_frame_for_faces(frame)

#             current_time = time.time()
            
#             if not self.known_face_encodings:
#                 # No known faces, trigger photo capture process
#                 self.speak("No known faces in the database. Would you like to add a new person?")
#                 if input("Add new person? (yes/no): ").lower() == 'yes':
#                     if self.take_photo():
#                         continue  # Return to main menu after successful photo capture
#                 else:
#                     self.speak("Exiting the program.")
#                     break

#             for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                 name, confidence = self.identify_person(face_encoding)
                
#                 # Calculate rough distance based on face box size
#                 face_size = bottom - top
#                 estimated_distance = round((1000 / face_size) * 0.3, 1)  # Rough estimation in meters

#                 # Draw face box and info
#                 color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
#                 cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
#                 # Add info text
#                 info_text = f"{name} ({confidence:.2f})"
#                 cv2.putText(frame, info_text, (left, top - 10), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#                 cv2.putText(frame, f"{estimated_distance}m", (left, bottom + 20),
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#                 # Speak updates with cooldown
#                 if name != "Unknown":
#                     if name not in self.last_greeting_time or \
#                        current_time - self.last_greeting_time[name] > self.greeting_cooldown:
#                         self.speak(f"{name} is {estimated_distance} meters in front of you.")
#                         self.last_greeting_time[name] = current_time
#                 else:
#                     # For unknown faces, trigger photo capture process
#                     self.speak("Unknown person detected. Would you like to add them?")
#                     if input("Add unknown person? (yes/no): ").lower() == 'yes':
#                         if self.take_photo():
#                             break  # Return to main menu after successful photo capture

#             cv2.imshow('Face Recognition', frame)
            
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.video_capture.release()
#         cv2.destroyAllWindows()

#     def cleanup(self):
#         """Cleanup resources."""
#         self.tts_queue.put(None)
#         self.tts_thread.join()
#         self.video_capture.release()
#         cv2.destroyAllWindows()

# # Usage example:
# if __name__ == "__main__":
#     system = FaceRecognitionSystem()
#     try:
#         # You can call either take_photo() or start_face_recognition()
#         system.start_face_recognition()
#     finally:
#         system.cleanup()