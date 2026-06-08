import cv2
from ultralytics import YOLO
import threading
import pygame
# import main

# Initialize pygame mixer
pygame.mixer.init()

# Load the pretrained YOLOv8 model
model = YOLO("src\\best.pt")  # Update with the correct path if needed

# Audio playback state
is_playing = False
current_audio = None

def play_audio(file):
    global is_playing, current_audio
    if not is_playing or (current_audio != file):
        is_playing = True
        current_audio = file
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing audio: {e}")
        is_playing = False

def get_frame_position(bbox, frame_width):
    x_center = bbox[0] + bbox[2] / 2
    if x_center < frame_width / 3:
        return 'left'
    elif x_center > 2 * frame_width / 3:
        return 'right'
    else:
        return 'center'

def assist_navigation(objects, frame_width):
    left, right, center = False, False, False
    guidance_text = "Path clear."
    audio_file = "src\\audio\\pathclear.mp3.mpeg"  # Updated path to the audio file

    for obj in objects:
        position = get_frame_position(obj['bbox'], frame_width)

        if position == 'left':
            left = True
        elif position == 'right':
            right = True
        elif position == 'center':
            center = True

    if center:
        guidance_text = "Obstacle directly ahead. Be cautious!"
        audio_file = "src\\audio\\obstacleahead.mp3.mpeg"
    elif left:
        guidance_text = "Obstacle on the left. Move right."
        audio_file = "src\\audio\\obstacleleft.mp3.mpeg"
    elif right:
        guidance_text = "Obstacle on the right. Move left."
        audio_file = "src\\audio\\obstacleright.mp3.mpeg"

    print(guidance_text)
    threading.Thread(target=play_audio, args=(audio_file,)).start()
    return guidance_text, left, center, right

def main():
    cap = cv2.VideoCapture(0)  # Update based on your system
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_height, frame_width = frame.shape[:2]

        results = model(frame)
        detected_objects = []

        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            confidence = box.conf[0]
            cls = int(box.cls[0])
            label = model.names[cls]

            if label in ['person', 'desk', 'stool', 'tv', 'chair', 'bed']:
                detected_objects.append({'label': label, 'bbox': (x1, y1, x2 - x1, y2 - y1)})

        guidance_text, left, center, right = assist_navigation(detected_objects, frame_width)

        # Visualization and frame display logic (same as your provided code)
        # Draw sections and bounding boxes...

        cv2.putText(frame, guidance_text, (10, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow('Smart Vision', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # import main
    # main.main()

if __name__ == "__main__":
    main()



# v - 0.2 ##################################################################################################################################


