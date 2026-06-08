
#v - 0.1 ####################################################################################################################

# import os
# import threading
# from models import walking_assistant, scenery_description  # Adjust import as needed
# from models.face_recognition import start_face_recognition, take_photo  # Ensure these functions are defined in the imported module

# def display_menu():
#     """Display the main menu options."""
#     print("Select an option:")
#     print("1. Walking Assistant")
#     print("2. Scenery Description")
#     print("3. Face Recognition")
#     print("4. Navigation")
#     print("5. Exit")

# def start_face_recognition_thread():
#     """Start the face recognition model in a separate thread."""
#     face_recognition_thread = threading.Thread(target=start_face_recognition)
#     face_recognition_thread.daemon = True  # Ensures thread closes when main exits
#     face_recognition_thread.start()

# def main():
#     print("Welcome to the AI Assistant!")
    
#     # Start the face recognition model in a separate thread
#     start_face_recognition_thread()

#     while True:
#         display_menu()
#         choice = input("Enter your choice (1-5): ").strip()

#         if choice == '1':
#             print("Starting Walking Assistant Model...")
#             walking_assistant.main()  # Call the walking assistant main function
#         elif choice == '2':
#             print("Starting Scenery Description Model...")
#             scenery_description.main()  # Call the scenery description main function
#         elif choice == '3':
#             take_photo()
#             print("Face Recognition Model is now active.")
#             # Since the face recognition runs in a thread, you can continue using the main thread
#         elif choice == '4':
#             print("Navigation model is not implemented yet.")
#             # Call the navigation function when implemented
#         elif choice == '5':
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please select a number between 1 and 5.")

# if __name__ == "__main__":
#     main()



#v - 0.2 ###################################################################################################################

# import threading
# import time
# import cv2
# import logging

# # Assuming your `face_recognition`, `take_photo`, `walking_assistant`, and `scenery_description` 
# # are defined functions within other imported modules or in this script.
# import os
# import threading
# from models import walking_assistant, scenery_description  # Adjust import as needed
# from models.face_recognition import start_face_recognition, take_photo  # Ensure these functions are defined in the imported module

# import pyttsx3

# # Initialize the TTS engine once globally
# engine = pyttsx3.init()
# tts_lock = threading.Lock()
# # Set up logging
# logging.basicConfig(level=logging.INFO)

# # Flags for running the threads
# walking_assistant_running = False
# scenery_description_running = False

# def speak(text):
#     with tts_lock:  # Use the lock to ensure exclusive access to the TTS engine
#         engine.say(text)
#         engine.runAndWait()



# def run_face_recognition():
#     """Run face recognition continuously in the background."""
#     start_face_recognition()  # This should run continuously on its own

# def run_walking_assistant():
#     """Run the walking assistant in a separate thread."""
#     global walking_assistant_running
#     walking_assistant_running = True
#     walking_assistant.main()

# def run_scenery_description():
#     """Run the scenery description in a separate thread."""
#     global scenery_description_running
#     scenery_description_running = True
#     scenery_description.main()

# def take_photo():
#     """Take a photo when option 3 is selected under face recognition."""
#     logging.info("Taking photo...")
#     # Your take_photo implementation goes here



# def main():
#     # Start face recognition in the background as soon as the program starts
#     threading.Thread(target=run_face_recognition, daemon=True).start()
#     logging.info("Face recognition model started.")

#     while True:
#         print("\nOptions:")
#         print("1. Start Walking Assistant")
#         print("2. Start Scenery Description")
#         print("3. Take Photo (Face Recognition)")
#         print("4. Exit")

#         choice = input("Choose an option: ")

#         if choice == '1':
#             if not walking_assistant_running:
#                 threading.Thread(target=run_walking_assistant, daemon=True).start()
#                 logging.info("Walking assistant started.")
#             else:
#                 logging.info("Walking assistant is already running.")

#         elif choice == '2':
#             if not scenery_description_running:
#                 threading.Thread(target=run_scenery_description, daemon=True).start()
#                 logging.info("Scenery description started.")
#             else:
#                 logging.info("Scenery description is already running.")

#         elif choice == '3':
#             take_photo()

#         elif choice == '4':
#             logging.info("Exiting program...")
#             break

#         else:
#             logging.warning("Invalid option. Please try again.")


# if __name__ == "__main__":
#     main()


# v - 0.3 #################################################################################
# import os
# import threading
# import logging
# import pyttsx3
# from queue import Queue
# from threading import Event

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Global flags and events
# running_tasks = {
#     'walking_assistant': False,
#     'scenery_description': False,
#     'face_recognition': False
# }

# stop_events = {
#     'walking_assistant': Event(),
#     'scenery_description': Event(),
#     'face_recognition': Event()
# }

# # Initialize the TTS engine
# engine = pyttsx3.init()
# tts_lock = threading.Lock()

# def speak(text):
#     """Thread-safe speaking function"""
#     with tts_lock:
#         engine.say(text)
#         engine.runAndWait()

# def run_face_recognition():
#     """Run face recognition in a controlled manner"""
#     from models.face_recognition import start_face_recognition
#     running_tasks['face_recognition'] = True
#     try:
#         while not stop_events['face_recognition'].is_set():
#             start_face_recognition()
#     except Exception as e:
#         logger.error(f"Face recognition error: {e}")
#     finally:
#         running_tasks['face_recognition'] = False

# def run_walking_assistant():
#     """Run walking assistant in a controlled manner"""
#     from models import walking_assistant
#     running_tasks['walking_assistant'] = True
#     try:
#         while not stop_events['walking_assistant'].is_set():
#             walking_assistant.main()
#     except Exception as e:
#         logger.error(f"Walking assistant error: {e}")
#     finally:
#         running_tasks['walking_assistant'] = False

# def run_scenery_description():
#     """Run scenery description in a controlled manner"""
#     from models import scenery_description
#     running_tasks['scenery_description'] = True
#     try:
#         while not stop_events['scenery_description'].is_set():
#             scenery_description.main()
#     except Exception as e:
#         logger.error(f"Scenery description error: {e}")
#     finally:
#         running_tasks['scenery_description'] = False

# def take_photo():
#     """Take a photo with proper error handling"""
#     from models.face_recognition import take_photo as face_photo
#     try:
#         face_photo()
#         logger.info("Photo taken successfully")
#     except Exception as e:
#         logger.error(f"Error taking photo: {e}")

# def display_menu():
#     """Display the main menu options"""
#     print("\nAI Assistant Menu:")
#     print("1. Start Walking Assistant")
#     print("2. Start Scenery Description")
#     print("3. Take Photo (Face Recognition)")
#     print("4. Stop Running Tasks")
#     print("5. Exit")
#     print("\nCurrently running tasks:")
#     for task, running in running_tasks.items():
#         status = "RUNNING" if running else "STOPPED"
#         print(f"- {task.replace('_', ' ').title()}: {status}")

# def stop_running_tasks():
#     """Stop all running tasks"""
#     for task, event in stop_events.items():
#         if running_tasks[task]:
#             event.set()
#             logger.info(f"Stopping {task}...")
    
#     # Wait for tasks to finish
#     while any(running_tasks.values()):
#         pass
    
#     # Reset stop events
#     for event in stop_events.values():
#         event.clear()

# def main():
#     """Main function with improved control flow"""
#     logger.info("Starting AI Assistant")
    
#     # Dictionary to store thread objects
#     threads = {}
    
#     try:
#         while True:
#             display_menu()
#             choice = input("\nEnter your choice (1-5): ").strip()  
#             if choice == '1':
#                 if not running_tasks['walking_assistant']:
#                     stop_events['walking_assistant'].clear()
#                     thread = threading.Thread(target=run_walking_assistant)
#                     thread.daemon = True
#                     thread.start()
#                     threads['walking_assistant'] = thread
#                     logger.info("Walking assistant started")
#                 else:
#                     logger.info("Walking assistant is already running")
            
#             elif choice == '2':
#                 if not running_tasks['scenery_description']:
#                     stop_events['scenery_description'].clear()
#                     thread = threading.Thread(target=run_scenery_description)
#                     thread.daemon = True
#                     thread.start()
#                     threads['scenery_description'] = thread
#                     logger.info("Scenery description started")
#                 else:
#                     logger.info("Scenery description is already running")
            
#             elif choice == '3':
#                 take_photo()
            
#             elif choice == '4':
#                 stop_running_tasks()
#                 logger.info("All tasks stopped")
            
#             elif choice == '5':
#                 logger.info("Exiting program...")
#                 stop_running_tasks()
#                 break
            
#             else:
#                 logger.warning("Invalid option. Please try again.")
            
#             # Small delay to prevent menu from refreshing too quickly
#             # threading.Event().wait(0.5)

#     except KeyboardInterrupt:
#         logger.info("Received keyboard interrupt")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#     finally:
#         stop_running_tasks()
#         logger.info("Program terminated")

# if __name__ == "__main__":
#     main()

# v - 0.4 #################################################################################################################################

import os
import threading
import logging
import pyttsx3
from queue import Queue
from threading import Event

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global flags and events
running_tasks = {
    'walking_assistant': False,
    'scenery_description': False,
    'face_recognition': False
}

stop_events = {
    'walking_assistant': Event(),
    'scenery_description': Event(),
    'face_recognition': Event()
}

# Initialize the TTS engine
engine = pyttsx3.init()
tts_lock = threading.Lock()

def speak(text):
    """Thread-safe speaking function"""
    with tts_lock:
        engine.say(text)
        engine.runAndWait()

def run_face_recognition():
    """Run face recognition in a controlled manner"""
    from models.face_recognition import start_face_recognition
    running_tasks['face_recognition'] = True
    try:
        while not stop_events['face_recognition'].is_set():
            start_face_recognition()
    except Exception as e:
        logger.error(f"Face recognition error: {e}")
    finally:
        running_tasks['face_recognition'] = False

def run_walking_assistant():
    """Run walking assistant in a controlled manner"""
    from models import walking_assistant
    running_tasks['walking_assistant'] = True
    try:
        while not stop_events['walking_assistant'].is_set():
            walking_assistant.main()
    except Exception as e:
        logger.error(f"Walking assistant error: {e}")
    finally:
        running_tasks['walking_assistant'] = False

def run_scenery_description():
    """Run scenery description in a controlled manner"""
    from models import scenery_description
    running_tasks['scenery_description'] = True
    try:
        while not stop_events['scenery_description'].is_set():
            scenery_description.main()
    except Exception as e:
        logger.error(f"Scenery description error: {e}")
    finally:
        running_tasks['scenery_description'] = False

def take_photo():
    """Take a photo with proper error handling"""
    from models.face_recognition import take_photo as face_photo
    try:
        face_photo()
        logger.info("Photo taken successfully")
    except Exception as e:
        logger.error(f"Error taking photo: {e}")

def display_menu():
    """Display the main menu options"""
    print("\nAI Assistant Menu:")
    print("1. Start Walking Assistant")
    print("2. Start Scenery Description")
    print("3. Take Photo (Face Recognition)")
    print("4. Stop Running Tasks")
    print("5. Exit")
    print("\nCurrently running tasks:")
    for task, running in running_tasks.items():
        status = "RUNNING" if running else "STOPPED"
        print(f"- {task.replace('_', ' ').title()}: {status}")

def stop_running_tasks():
    """Stop all running tasks and wait for them to finish"""
    for task, event in stop_events.items():
        if running_tasks[task]:
            event.set()  # Signal the task to stop
            logger.info(f"Stopping {task}...")

    # Wait for tasks to finish
    for task, thread in threads.items():
        if thread.is_alive():
            thread.join()  # Wait for the thread to complete
            logger.info(f"{task.replace('_', ' ').title()} has stopped.")

    # Reset stop events
    for event in stop_events.values():
        event.clear()

def main():
    """Main function with improved control flow"""
    logger.info("Starting AI Assistant")

    # Dictionary to store thread objects
    global threads
    threads = {}

    try:
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-5): ").strip()  
            
            if choice == '1':
                if not running_tasks['walking_assistant']:
                    stop_events['walking_assistant'].clear()
                    thread = threading.Thread(target=run_walking_assistant)
                    thread.start()
                    threads['walking_assistant'] = thread
                    thread.join()  # Wait for the thread to finish
                    logger.info("Walking assistant stopped")
                else:
                    logger.info("Walking assistant is already running")
            
            elif choice == '2':
                if not running_tasks['scenery_description']:
                    stop_events['scenery_description'].clear()
                    thread = threading.Thread(target=run_scenery_description)
                    thread.start()
                    threads['scenery_description'] = thread
                    thread.join()  # Wait for the thread to finish
                    logger.info("Scenery description stopped")
                else:
                    logger.info("Scenery description is already running")
            
            elif choice == '3':
                # # face_recognition_system.take_photo()
                from models.face_recognition import take_photo
                take_photo()
                


            elif choice == '4':
                stop_running_tasks()
                logger.info("All tasks stopped")
            
            elif choice == '5':
                logger.info("Exiting program...")
                stop_running_tasks()
                break
            
            else:
                logger.warning("Invalid option. Please try again.")
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        stop_running_tasks()
        logger.info("Program terminated")

if __name__ == "__main__":
    main()
