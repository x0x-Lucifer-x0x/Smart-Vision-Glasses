# import cv2
# import numpy as np
# import time
# import os
# import threading
# import queue
# from gtts import gTTS
# import pygame
# import easyocr
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import NMF
# from nltk.tokenize import sent_tokenize
# import nltk
 
# # Ensure necessary NLTK data is downloaded
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')

# class ReadingAssistant:
#     def __init__(self):
#         self.camera = None
#         self.is_running = False
#         self.text_queue = queue.Queue()
#         self.last_processed_time = 0
#         self.processing_interval = 2  # Process frames every 2 seconds
#         self.previous_text = ""
#         self.current_text = ""
#         self.current_summary = ""
#         self.display_text = ""
        
#         # Initialize OCR reader (only once to save memory)
#         print("Initializing EasyOCR (this may take a moment)...")
#         self.reader = easyocr.Reader(['en'], gpu=False)
#         print("EasyOCR initialized successfully!")
        
#         self.initialize_audio()
        
#     def initialize_audio(self):
#         """Initialize pygame for audio playback"""
#         pygame.mixer.init()
        
#     def initialize_camera(self):
#         """Initialize the camera for capturing live video feed."""
#         self.camera = cv2.VideoCapture(0)
#         if not self.camera.isOpened():
#             print("Could not open camera. Trying alternative camera index...")
#             self.camera = cv2.VideoCapture(1)  # Try alternative camera
#             if not self.camera.isOpened():
#                 raise Exception("Error: Could not open any camera.")
        
#         # Set camera resolution for better text recognition
#         self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#         self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#         return True
            
#     def extract_text(self, frame):
#         """Extract text from the captured frame using EasyOCR."""
#         try:
#             # Pre-process the frame to improve text detection
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
#             # Apply CLAHE for better contrast
#             clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#             gray = clahe.apply(gray)
            
#             # Perform text detection with EasyOCR
#             results = self.reader.readtext(gray)
            
#             # Extract text from results
#             texts = [result[1] for result in results]
#             full_text = " ".join(texts)
            
#             if full_text.strip():
#                 print("\nDetected Raw Text:")
#                 print(full_text[:150] + "..." if len(full_text) > 150 else full_text)
                
#                 # Draw bounding boxes on the frame (for debugging/visualization)
#                 for (bbox, text, prob) in results:
#                     # Convert bbox to points format required by cv2.rectangle
#                     (top_left, top_right, bottom_right, bottom_left) = bbox
#                     top_left = (int(top_left[0]), int(top_left[1]))
#                     bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                    
#                     # Draw rectangle
#                     cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            
#             return full_text
            
#         except Exception as e:
#             print(f"OCR Error: {e}")
#             return ""
    
#     def summarize_text(self, text, max_sentences=3):
#         """Generate a summary of the extracted text."""
#         # Return text directly if it's too short
#         if len(text.strip()) < 50:
#             return text
            
#         # Break text into sentences
#         sentences = sent_tokenize(text)
#         if len(sentences) <= max_sentences:
#             return text
            
#         # Use TF-IDF vectorization
#         try:
#             vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')
#             tfidf = vectorizer.fit_transform(sentences)
            
#             # Use Non-negative Matrix Factorization for topic extraction
#             nmf = NMF(n_components=1, random_state=42).fit(tfidf)
#             feature_names = vectorizer.get_feature_names_out()
            
#             # Get important words
#             topic_words = [feature_names[i] for i in nmf.components_[0].argsort()[:-10:-1]]
            
#             # Score sentences by presence of important words
#             scores = []
#             for sentence in sentences:
#                 score = sum([1 for word in topic_words if word.lower() in sentence.lower()])
#                 scores.append(score)
                
#             # Get top sentences
#             ranked_sentences = sorted(((scores[i], i) for i in range(len(sentences))), 
#                                        reverse=True)
            
#             # Prepare summary using original sentence order
#             selected_indices = sorted([idx for _, idx in ranked_sentences[:max_sentences]])
#             summary = " ".join([sentences[i] for i in selected_indices])
            
#             print("\nSummarized Text:")
#             print(summary)
#             return summary
            
#         except Exception as e:
#             print(f"Summarization error: {e}")
#             # Fall back to first few sentences if analysis fails
#             return " ".join(sentences[:max_sentences])
    
#     def speak_text(self, text):
#         """Convert text to speech."""
#         if not text.strip():
#             return False
            
#         try:
#             # Stop any currently playing audio
#             if pygame.mixer.music.get_busy():
#                 pygame.mixer.music.stop()
            
#             tts = gTTS(text=text, lang='en', slow=False)
#             output_file = "output.mp3"
#             tts.save(output_file)
            
#             # Play audio using pygame
#             pygame.mixer.music.load(output_file)
#             pygame.mixer.music.play()
            
#             print("\nSpeaking Text:")
#             print(text)
#             return True
#         except Exception as e:
#             print(f"TTS Error: {e}")
#             return False
    
#     def process_text_queue(self):
#         """Process text from the queue and speak it."""
#         while self.is_running:
#             try:
#                 text = self.text_queue.get(timeout=1)
                
#                 # Only process if the text is not empty
#                 if text.strip():
#                     # Check if text is different enough from previous text
#                     if self._text_difference(text, self.previous_text) > 0.3:
#                         self.current_text = text
#                         self.current_summary = self.summarize_text(text)
#                         self.display_text = self.current_summary
                        
#                         # Speak the summarized text
#                         success = self.speak_text(self.current_summary)
#                         if success:
#                             self.previous_text = text
                
#                 self.text_queue.task_done()
#             except queue.Empty:
#                 pass
#             except Exception as e:
#                 print(f"Processing error: {e}")
    
#     def _text_difference(self, text1, text2):
#         """Calculate how different two texts are (0-1 scale)."""
#         if not text1 or not text2:
#             return 1.0
            
#         # Simple difference measure based on words
#         words1 = set(text1.lower().split())
#         words2 = set(text2.lower().split())
        
#         union = len(words1.union(words2))
#         if union == 0:
#             return 0
            
#         intersection = len(words1.intersection(words2))
#         return 1 - (intersection / union)
    
#     def add_caption_to_frame(self, frame, text):
#         """Add caption text to the bottom of the frame."""
#         if not text.strip():
#             return frame
            
#         # Create a semi-transparent black background for better text visibility
#         h, w = frame.shape[:2]
#         overlay = frame.copy()
        
#         # Calculate how many lines we need based on text length
#         text_length = len(text)
#         chars_per_line = w // 10  # Approximate
#         num_lines = max(1, text_length // chars_per_line)
#         caption_height = min(h // 3, 30 * num_lines)  # Cap at 1/3 of frame height
        
#         # Draw background rectangle
#         cv2.rectangle(overlay, (0, h - caption_height), (w, h), (0, 0, 0), -1)
        
#         # Add semi-transparency
#         alpha = 0.7
#         frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
#         # Format text to fit width
#         formatted_text = []
#         words = text.split()
#         current_line = ""
        
#         for word in words:
#             if len(current_line + " " + word) <= chars_per_line:
#                 current_line += " " + word if current_line else word
#             else:
#                 formatted_text.append(current_line)
#                 current_line = word
                
#         if current_line:
#             formatted_text.append(current_line)
        
#         # Display only the first few lines to fit in the caption area
#         max_visible_lines = caption_height // 30
#         visible_text = formatted_text[:max_visible_lines]
        
#         # Add text
#         for i, line in enumerate(visible_text):
#             y_pos = h - caption_height + (i + 1) * 30
#             cv2.putText(frame, line, (10, y_pos), 
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
#         return frame
    
#     def start(self):
#         """Start the reading assistant."""
#         if self.is_running:
#             print("Reading assistant is already running.")
#             return
            
#         self.is_running = True
        
#         # Initialize camera
#         if not self.initialize_camera():
#             return
            
#         # Start the text processing thread
#         threading.Thread(target=self.process_text_queue, daemon=True).start()
        
#         print("Reading assistant started. Press 'q' to quit.")
#         print("Waiting for text to be detected...")
        
#         try:
#             while self.is_running:
#                 # Capture frame
#                 ret, frame = self.camera.read()
#                 if not ret:
#                     print("Error capturing frame.")
#                     break
                
#                 # Add caption to the frame if we have text
#                 if self.display_text:
#                     frame = self.add_caption_to_frame(frame, self.display_text)
                
#                 # Display the frame
#                 cv2.imshow('Reading Assistant - Press Q to quit', frame)
                
#                 # Process frame at intervals
#                 current_time = time.time()
#                 if current_time - self.last_processed_time >= self.processing_interval:
#                     self.last_processed_time = current_time
                    
#                     # Extract text in a separate thread to avoid blocking
#                     def process_frame(frame):
#                         text = self.extract_text(frame.copy())
#                         if text.strip():
#                             self.text_queue.put(text)
                    
#                     threading.Thread(target=process_frame, args=(frame.copy(),)).start()
                
#                 # Check for quit command
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
                    
#         finally:
#             self.stop()
    
#     def stop(self):
#         """Stop the reading assistant."""
#         self.is_running = False
        
#         if self.camera is not None:
#             self.camera.release()
            
#         # Clean up pygame
#         pygame.mixer.quit()
        
#         cv2.destroyAllWindows()
#         print("Reading assistant stopped.")

# if __name__ == "__main__":
#     print("Starting Reading Assistant for Blind Users...")
    
#     try:
#         assistant = ReadingAssistant()
#         assistant.start()
#     except KeyboardInterrupt:
#         print("\nProgram interrupted by user.")
#     except Exception as e:
#         print(f"Error: {e}")
#         print("\nTroubleshooting tips:")
#         print("1. Make sure your camera is connected and functioning")
#         print("2. Ensure you have sufficient lighting for text recognition")
#         print("3. Check that all required packages are installed")
#         input("\nPress Enter to exit...")

#version 2.0........................................................................................................
# import cv2
# import numpy as np
# import threading
# import queue
# import time
# import os
# import pygame
# from gtts import gTTS
# import easyocr
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import NMF
# from nltk.tokenize import sent_tokenize
# import nltk

# # Ensure necessary NLTK data is downloaded
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt', quiet=True)

# class OptimizedReadingAssistant:
#     def __init__(self):
#         # Core components
#         self.camera = None
#         self.is_running = False
#         self.frame_queue = queue.Queue(maxsize=2)  # Limit frame queue size
#         self.text_queue = queue.Queue()
#         self.processed_results = {}  # Store processed results
        
#         # Timing control
#         self.processing_interval = 1.0  # Process frames every second
#         self.last_capture_time = 0
#         self.fps_counter = 0
#         self.fps_timer = time.time()
#         self.fps = 0
        
#         # Display settings
#         self.width = 1280
#         self.height = 720
#         self.show_debug = True
        
#         # State tracking
#         self.current_text = ""
#         self.current_summary = ""
#         self.previous_text = ""
        
#         # Initialize pygame for display and audio
#         pygame.init()
#         pygame.mixer.init()
#         self.screen = pygame.display.set_mode((self.width, self.height))
#         pygame.display.set_caption("Optimized Reading Assistant - Press ESC to quit")
#         self.font = pygame.font.SysFont("Arial", 24)
#         self.small_font = pygame.font.SysFont("Arial", 16)
        
#         # Initialize OCR in a separate thread to not block startup
#         self.reader = None
#         threading.Thread(target=self._init_ocr, daemon=True).start()
        
#     def _init_ocr(self):
#         """Initialize OCR engine in background thread"""
#         print("Initializing EasyOCR engine (this may take a moment)...")
#         self.reader = easyocr.Reader(['en'], gpu=False, quantize=True)  # Use quantization for speed
#         print("EasyOCR initialized successfully!")
        
#     def wait_for_ocr_init(self):
#         """Wait for OCR initialization to complete"""
#         while self.reader is None:
#             print("Waiting for OCR engine to initialize...")
#             time.sleep(1)
    
#     def initialize_camera(self):
#         """Initialize the camera with optimal settings for text detection"""
#         self.camera = cv2.VideoCapture(0)
#         if not self.camera.isOpened():
#             print("Could not open primary camera. Trying alternative...")
#             self.camera = cv2.VideoCapture(1)
#             if not self.camera.isOpened():
#                 raise Exception("No camera available")
        
#         # Configure camera for optimal text detection
#         self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
#         self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
#         self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Enable auto exposure
#         self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)      # Enable autofocus if available
        
#         # Warm up camera
#         for _ in range(5):
#             self.camera.read()
            
#         return True
    
#     def capture_frames(self):
#         """Continuously capture frames from camera"""
#         while self.is_running:
#             ret, frame = self.camera.read()
#             if not ret:
#                 print("Failed to capture frame")
#                 time.sleep(0.1)
#                 continue
            
#             # Update FPS counter
#             self.fps_counter += 1
#             if time.time() - self.fps_timer >= 1.0:
#                 self.fps = self.fps_counter
#                 self.fps_counter = 0
#                 self.fps_timer = time.time()
            
#             # Only queue a new frame if current time exceeds the interval
#             current_time = time.time()
#             if current_time - self.last_capture_time >= self.processing_interval:
#                 # Skip if queue is full (prevents backlog)
#                 if self.frame_queue.full():
#                     try:
#                         self.frame_queue.get_nowait()  # Remove old frame
#                     except queue.Empty:
#                         pass
                
#                 # Add new frame for processing
#                 try:
#                     self.frame_queue.put_nowait(frame.copy())
#                     self.last_capture_time = current_time
#                 except queue.Full:
#                     pass  # Skip if still full
    
#     def process_frames(self):
#         """Process frames from queue and extract text"""
#         while self.is_running:
#             if self.reader is None:
#                 time.sleep(0.5)  # Wait for OCR to initialize
#                 continue
                
#             try:
#                 frame = self.frame_queue.get(timeout=0.5)
                
#                 # Preprocessing for better OCR results
#                 processed_frame = self._preprocess_image(frame)
                
#                 # Extract text in this thread
#                 extracted_text, annotated_frame = self._extract_text(processed_frame, frame)
                
#                 # Update processed results
#                 if extracted_text.strip():
#                     self.processed_results = {
#                         'text': extracted_text,
#                         'frame': annotated_frame,
#                         'timestamp': time.time()
#                     }
                    
#                     # Only add to text queue if text is significant
#                     if len(extracted_text) > 5:
#                         self.text_queue.put(extracted_text)
                        
#                 self.frame_queue.task_done()
                
#             except queue.Empty:
#                 pass  # No frames to process
    
#     def process_text(self):
#         """Process extracted text for summarization and speech"""
#         while self.is_running:
#             try:
#                 text = self.text_queue.get(timeout=0.5)
                
#                 # Only process text that is significantly different from previous
#                 if self._text_difference(text, self.previous_text) > 0.3:
#                     # Update state
#                     self.current_text = text
                    
#                     # Generate summary
#                     start_time = time.time()
#                     self.current_summary = self._summarize_text(text)
#                     summary_time = time.time() - start_time
                    
#                     if self.show_debug:
#                         print(f"Summarization took {summary_time:.2f}s")
                    
#                     # Speak the text if significantly different
#                     self._speak_text(self.current_summary)
#                     self.previous_text = text
                
#                 self.text_queue.task_done()
                
#             except queue.Empty:
#                 pass  # No text to process
    
#     def _preprocess_image(self, frame):
#         """Preprocess image for better OCR results"""
#         # Convert to grayscale
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
#         # Apply CLAHE for better contrast
#         clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#         enhanced = clahe.apply(gray)
        
#         # Apply light gaussian blur to reduce noise
#         blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
#         # Adaptive thresholding for better text detection
#         thresh = cv2.adaptiveThreshold(
#             blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#             cv2.THRESH_BINARY_INV, 11, 2
#         )
        
#         # Invert the image back to get black text on white background
#         thresh = cv2.bitwise_not(thresh)
        
#         return thresh
    
#     def _extract_text(self, processed_image, original_frame):
#         """Extract text from preprocessed image"""
#         try:
#             # Define confidence threshold for OCR
#             confidence_threshold = 0.4
            
#             # Use low resolution for faster processing
#             scaled_img = cv2.resize(processed_image, None, fx=0.5, fy=0.5)
            
#             # Use smaller paragraph threshold for better segmentation
#             results = self.reader.readtext(
#                 scaled_img,
#                 paragraph=False,  # Don't merge text in paragraphs
#                 detail=1,
#                 adjust_contrast=0.8,
#                 width_ths=0.5,
#                 height_ths=0.5
#             )
            
#             # Scale detection coordinates back to original size
#             scaled_results = []
#             for (bbox, text, prob) in results:
#                 if prob >= confidence_threshold:
#                     # Scale back bounding box coordinates
#                     scaled_bbox = [[x*2, y*2] for x, y in bbox]
#                     scaled_results.append((scaled_bbox, text, prob))
            
#             # Draw bounding boxes on the original frame
#             annotated_frame = original_frame.copy()
            
#             # Extract text and annotate the frame
#             texts = []
#             for (bbox, text, prob) in scaled_results:
#                 # Append text
#                 texts.append(text)
                
#                 # Convert bbox to integer points
#                 pts = np.array(bbox, np.int32)
#                 pts = pts.reshape((-1, 1, 2))
                
#                 # Draw filled polygon with transparency
#                 overlay = annotated_frame.copy()
#                 cv2.fillPoly(overlay, [pts.reshape((-1, 2))], (0, 255, 0, 0.3))
                
#                 # Add the overlay with transparency
#                 alpha = 0.2
#                 annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1-alpha, 0)
                
#                 # Draw outline
#                 cv2.polylines(annotated_frame, [pts.reshape((-1, 2))], True, (0, 255, 0), 2)
                
#                 # Add text label
#                 text_pos = (int(pts[0][0][0]), int(pts[0][0][1]) - 10)
#                 cv2.putText(
#                     annotated_frame, f"{text} ({prob:.2f})", text_pos,
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
#                 )
            
#             # Join the texts with proper spacing
#             full_text = " ".join(texts)
            
#             # If debug is enabled and text was found, print it
#             if self.show_debug and full_text.strip():
#                 print(f"Detected raw text: {full_text[:150]}...")
            
#             return full_text, annotated_frame
            
#         except Exception as e:
#             print(f"OCR Error: {e}")
#             return "", original_frame
    
#     def _summarize_text(self, text, max_sentences=3):
#         """Summarize text to extract most important points"""
#         # Return text directly if it's short
#         if len(text.strip()) < 100:
#             return text
            
#         # Tokenize into sentences
#         try:
#             sentences = sent_tokenize(text)
#             if len(sentences) <= max_sentences:
#                 return text
                
#             # Use TF-IDF for better sentence ranking
#             vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')
#             tfidf = vectorizer.fit_transform(sentences)
            
#             # Use NMF for topic extraction
#             nmf = NMF(n_components=1, random_state=42).fit(tfidf)
#             feature_names = vectorizer.get_feature_names_out()
            
#             # Get important words
#             topic_words = [feature_names[i] for i in nmf.components_[0].argsort()[:-10:-1]]
            
#             # Score sentences by presence of important words
#             scores = []
#             for sentence in sentences:
#                 score = sum([1 for word in topic_words if word.lower() in sentence.lower()])
#                 scores.append(score)
                
#             # Get top sentences
#             ranked_sentences = sorted(((scores[i], i) for i in range(len(sentences))), 
#                                     reverse=True)
            
#             # Prepare summary using original sentence order
#             selected_indices = sorted([idx for _, idx in ranked_sentences[:max_sentences]])
#             summary = " ".join([sentences[i] for i in selected_indices])
            
#             if self.show_debug:
#                 print(f"Summarized text: {summary}")
                
#             return summary
            
#         except Exception as e:
#             print(f"Summarization error: {e}")
#             # Fall back to first few sentences
#             sentences = text.split('.')
#             return '. '.join(sentences[:max_sentences]) + '.'
    
#     def _speak_text(self, text):
#         """Convert text to speech"""
#         if not text.strip():
#             return False
            
#         try:
#             # Stop any currently playing audio
#             if pygame.mixer.music.get_busy():
#                 pygame.mixer.music.stop()
            
#             # Create a temporary filename based on text hash to avoid regenerating same audio
#             text_hash = hash(text) % 100000
#             output_file = f"audio_cache_{text_hash}.mp3"
            
#             # Only generate audio if it doesn't exist
#             if not os.path.exists(output_file):
#                 tts = gTTS(text=text, lang='en', slow=False)
#                 tts.save(output_file)
            
#             # Play audio
#             pygame.mixer.music.load(output_file)
#             pygame.mixer.music.play()
            
#             if self.show_debug:
#                 print(f"Speaking text: {text[:100]}...")
                
#             return True
            
#         except Exception as e:
#             print(f"TTS Error: {e}")
#             return False
    
#     def _text_difference(self, text1, text2):
#         """Calculate how different two texts are (0-1 scale)"""
#         if not text1 or not text2:
#             return 1.0
            
#         # Simple difference measure based on words
#         words1 = set(text1.lower().split())
#         words2 = set(text2.lower().split())
        
#         union = len(words1.union(words2))
#         if union == 0:
#             return 0
            
#         intersection = len(words1.intersection(words2))
#         return 1 - (intersection / union)
    
#     def _convert_frame_to_pygame(self, frame):
#         """Convert OpenCV frame to Pygame surface correctly"""
#         if frame is None:
#             # Create a black frame if no frame is available
#             empty = np.zeros((self.height, self.width, 3), dtype=np.uint8)
#             frame = empty
        
#         # Convert from BGR (OpenCV) to RGB (Pygame)
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
#         # Create the pygame surface directly
#         surface = pygame.surfarray.make_surface(np.transpose(rgb_frame, (1, 0, 2)))
            
#         return surface
    
#     def _render_text(self, surface, text, position=(10, 10), max_width=None, color=(255, 255, 255)):
#         """Render text with word wrapping"""
#         if not text.strip():
#             return 0
            
#         if max_width is None:
#             max_width = self.width - 20
            
#         words = text.split()
#         lines = []
#         current_line = []
        
#         for word in words:
#             test_line = ' '.join(current_line + [word])
#             text_surface = self.font.render(test_line, True, color)
            
#             if text_surface.get_width() < max_width:
#                 current_line.append(word)
#             else:
#                 if current_line:  # Avoid empty lines
#                     lines.append(' '.join(current_line))
#                 current_line = [word]
                
#         if current_line:
#             lines.append(' '.join(current_line))
            
#         total_height = 0
#         for i, line in enumerate(lines):
#             text_surface = self.font.render(line, True, color)
#             y_pos = position[1] + i * (self.font.get_height() + 2)
#             surface.blit(text_surface, (position[0], y_pos))
#             total_height = y_pos + text_surface.get_height() - position[1]
            
#         return total_height
    
#     def _render_info_overlay(self, surface):
#         """Render performance metrics and debug info"""
#         # Create semi-transparent overlay
#         overlay = pygame.Surface((220, 100))
#         overlay.set_alpha(180)
#         overlay.fill((0, 0, 0))
#         surface.blit(overlay, (self.width - 230, 10))
        
#         # Render FPS
#         fps_text = self.small_font.render(f"FPS: {self.fps}", True, (255, 255, 255))
#         surface.blit(fps_text, (self.width - 220, 15))
        
#         # Render OCR status
#         if self.reader is None:
#             status_text = self.small_font.render("OCR: Initializing...", True, (255, 150, 50))
#         else:
#             status_text = self.small_font.render("OCR: Ready", True, (100, 255, 100))
#         surface.blit(status_text, (self.width - 220, 35))
        
#         # Render processing interval
#         interval_text = self.small_font.render(f"Process interval: {self.processing_interval:.1f}s", True, (255, 255, 255))
#         surface.blit(interval_text, (self.width - 220, 55))
        
#         # Display shortcuts
#         help_text = self.small_font.render("Press 'F': Faster, 'S': Slower", True, (200, 200, 200))
#         surface.blit(help_text, (self.width - 220, 75))
    
#     def _render_text_overlay(self, surface):
#         """Render the detected text overlay"""
#         if not self.current_summary:
#             return
            
#         # Create semi-transparent overlay
#         height = min(200, self.height // 3)
#         overlay = pygame.Surface((self.width, height))
#         overlay.set_alpha(180)
#         overlay.fill((0, 0, 0))
#         surface.blit(overlay, (0, self.height - height))
        
#         # Render summary text
#         self._render_text(
#             surface, 
#             self.current_summary, 
#             position=(10, self.height - height + 10),
#             max_width=self.width - 20,
#             color=(255, 255, 255)
#         )
    
#     def start(self):
#         """Start the reading assistant"""
#         if self.is_running:
#             print("Reading assistant is already running")
#             return
            
#         self.is_running = True
        
#         # Wait for OCR to initialize
#         self.wait_for_ocr_init()
        
#         # Initialize camera
#         if not self.initialize_camera():
#             self.is_running = False
#             return
        
#         # Start worker threads
#         threading.Thread(target=self.capture_frames, daemon=True).start()
#         threading.Thread(target=self.process_frames, daemon=True).start()
#         threading.Thread(target=self.process_text, daemon=True).start()
        
#         print("Reading assistant started. Press ESC to quit.")
        
#         clock = pygame.time.Clock()
#         try:
#             while self.is_running:
#                 # Handle events
#                 for event in pygame.event.get():
#                     if event.type == pygame.QUIT:
#                         self.is_running = False
#                     elif event.type == pygame.KEYDOWN:
#                         if event.key == pygame.K_ESCAPE:
#                             self.is_running = False
#                         elif event.key == pygame.K_f:  # Faster processing
#                             self.processing_interval = max(0.2, self.processing_interval - 0.2)
#                             print(f"Processing interval: {self.processing_interval:.1f}s")
#                         elif event.key == pygame.K_s:  # Slower processing
#                             self.processing_interval = min(3.0, self.processing_interval + 0.2)
#                             print(f"Processing interval: {self.processing_interval:.1f}s")
                
#                 # Clear screen
#                 self.screen.fill((0, 0, 0))
                
#                 # Get latest processed frame if available
#                 if 'frame' in self.processed_results:
#                     frame = self.processed_results['frame']
#                     # Convert and display the frame
#                     pygame_surface = self._convert_frame_to_pygame(frame)
#                     self.screen.blit(pygame_surface, (0, 0))
#                 else:
#                     # Capture and display camera feed even without processing
#                     ret, frame = self.camera.read()
#                     if ret:
#                         pygame_surface = self._convert_frame_to_pygame(frame)
#                         self.screen.blit(pygame_surface, (0, 0))
                
#                 # Render text overlay if we have summarized text
#                 self._render_text_overlay(self.screen)
                
#                 # Render debug information
#                 if self.show_debug:
#                     self._render_info_overlay(self.screen)
                
#                 # Update display
#                 pygame.display.flip()
                
#                 # Control frame rate
#                 clock.tick(30)
                
#         finally:
#             self.stop()
    
#     def stop(self):
#         """Stop the reading assistant"""
#         self.is_running = False
        
#         # Wait for threads to finish
#         time.sleep(0.5)
        
#         # Release resources
#         if self.camera is not None:
#             self.camera.release()
            
#         # Clean up pygame
#         pygame.quit()
        
#         # Remove temporary audio files
#         for file in os.listdir():
#             if file.startswith("audio_cache_") and file.endswith(".mp3"):
#                 try:
#                     os.remove(file)
#                 except:
#                     pass
        
#         print("Reading assistant stopped.")

# if __name__ == "__main__":
#     print("Starting Optimized Real-time Reading Assistant...")
    
#     try:
#         assistant = OptimizedReadingAssistant()
#         assistant.start()
#     except KeyboardInterrupt:
#         print("\nProgram interrupted by user.")
#     except Exception as e:
#         print(f"Error: {e}")
#         print("\nTroubleshooting tips:")
#         print("1. Make sure your camera is connected and functioning")
#         print("2. Ensure you have sufficient lighting for text recognition")
#         print("3. Check that all required packages are installed")
#         input("\nPress Enter to exit...")

#version 3.0..................................................................................................................

import cv2
import numpy as np
import threading
import queue
import time
import os
import pygame
from gtts import gTTS
import easyocr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.tokenize import sent_tokenize
import nltk

# Ensure necessary NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class OptimizedReadingAssistant:
    def __init__(self):
        # Core components
        self.camera = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=2)  # Limit frame queue size
        self.text_queue = queue.Queue()
        self.processed_results = {}  # Store processed results
        
        # Timing control
        self.processing_interval = 1.0  # Process frames every second
        self.last_capture_time = 0
        self.fps_counter = 0
        self.fps_timer = time.time()
        self.fps = 0
        
        # Display settings
        self.width = 1280
        self.height = 720
        self.show_debug = True
        
        # State tracking
        self.current_text = ""
        self.current_summary = ""
        self.previous_text = ""
        
        # Initialize pygame for display and audio
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Optimized Reading Assistant - Press ESC to quit")
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # Initialize OCR in a separate thread to not block startup
        self.reader = None
        threading.Thread(target=self._init_ocr, daemon=True).start()
        
    def _init_ocr(self):
        """Initialize OCR engine in background thread"""
        print("Initializing EasyOCR engine (this may take a moment)...")
        self.reader = easyocr.Reader(['en'], gpu=False, quantize=True)  # Use quantization for speed
        print("EasyOCR initialized successfully!")
        
    def wait_for_ocr_init(self):
        """Wait for OCR initialization to complete"""
        while self.reader is None:
            print("Waiting for OCR engine to initialize...")
            time.sleep(1)
    
    def initialize_camera(self):
        """Initialize the camera with optimal settings for text detection"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Could not open primary camera. Trying alternative...")
            self.camera = cv2.VideoCapture(1)
            if not self.camera.isOpened():
                raise Exception("No camera available")
        
        # Configure camera for optimal text detection
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Enable auto exposure
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)      # Enable autofocus if available
        
        # Warm up camera
        for _ in range(5):
            self.camera.read()
            
        return True
    
    def capture_frames(self):
        """Continuously capture frames from camera"""
        while self.is_running:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to capture frame")
                time.sleep(0.1)
                continue
            
            # Update FPS counter
            self.fps_counter += 1
            if time.time() - self.fps_timer >= 1.0:
                self.fps = self.fps_counter
                self.fps_counter = 0
                self.fps_timer = time.time()
            
            # Only queue a new frame if current time exceeds the interval
            current_time = time.time()
            if current_time - self.last_capture_time >= self.processing_interval:
                # Skip if queue is full (prevents backlog)
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()  # Remove old frame
                    except queue.Empty:
                        pass
                
                # Add new frame for processing
                try:
                    self.frame_queue.put_nowait(frame.copy())
                    self.last_capture_time = current_time
                except queue.Full:
                    pass  # Skip if still full
    
    def process_frames(self):
        """Process frames from queue and extract text"""
        while self.is_running:
            if self.reader is None:
                time.sleep(0.5)  # Wait for OCR to initialize
                continue
                
            try:
                frame = self.frame_queue.get(timeout=0.5)
                
                # Preprocessing for better OCR results
                processed_frame = self._preprocess_image(frame)
                
                # Extract text in this thread
                extracted_text, annotated_frame = self._extract_text(processed_frame, frame)
                
                # Update processed results
                if extracted_text.strip():
                    self.processed_results = {
                        'text': extracted_text,
                        'frame': annotated_frame,
                        'timestamp': time.time()
                    }
                    
                    # Only add to text queue if text is significant
                    if len(extracted_text) > 5:
                        self.text_queue.put(extracted_text)
                        
                self.frame_queue.task_done()
                
            except queue.Empty:
                pass  # No frames to process
    
    def process_text(self):
        """Process extracted text for summarization and speech"""
        while self.is_running:
            try:
                text = self.text_queue.get(timeout=0.5)
                
                # Only process text that is significantly different from previous
                if self._text_difference(text, self.previous_text) > 0.3:
                    # Update state
                    self.current_text = text
                    
                    # Generate summary
                    start_time = time.time()
                    self.current_summary = self._summarize_text(text)
                    summary_time = time.time() - start_time
                    
                    if self.show_debug:
                        print(f"Summarization took {summary_time:.2f}s")
                    
                    # Speak the text if significantly different
                    self._speak_text(self.current_summary)
                    self.previous_text = text
                
                self.text_queue.task_done()
                
            except queue.Empty:
                pass  # No text to process
    
    def _preprocess_image(self, frame):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply light gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Adaptive thresholding for better text detection
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Invert the image back to get black text on white background
        thresh = cv2.bitwise_not(thresh)
        
        return thresh
    
    def _extract_text(self, processed_image, original_frame):
        """Extract text from preprocessed image"""
        try:
            # Define confidence threshold for OCR
            confidence_threshold = 0.4
            
            # Use low resolution for faster processing
            scaled_img = cv2.resize(processed_image, None, fx=0.5, fy=0.5)
            
            # Use smaller paragraph threshold for better segmentation
            results = self.reader.readtext(
                scaled_img,
                paragraph=False,  # Don't merge text in paragraphs
                detail=1,
                adjust_contrast=0.8,
                width_ths=0.5,
                height_ths=0.5
            )
            
            # Scale detection coordinates back to original size
            scaled_results = []
            for (bbox, text, prob) in results:
                if prob >= confidence_threshold:
                    # Scale back bounding box coordinates
                    scaled_bbox = [[x*2, y*2] for x, y in bbox]
                    scaled_results.append((scaled_bbox, text, prob))
            
            # Draw bounding boxes on the original frame
            annotated_frame = original_frame.copy()
            
            # Extract text and annotate the frame
            texts = []
            for (bbox, text, prob) in scaled_results:
                # Append text
                texts.append(text)
                
                # Convert bbox to integer points
                pts = np.array(bbox, np.int32)
                pts = pts.reshape((-1, 1, 2))
                
                # Draw filled polygon with transparency
                overlay = annotated_frame.copy()
                cv2.fillPoly(overlay, [pts.reshape((-1, 2))], (0, 255, 0, 0.3))
                
                # Add the overlay with transparency
                alpha = 0.2
                annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1-alpha, 0)
                
                # Draw outline
                cv2.polylines(annotated_frame, [pts.reshape((-1, 2))], True, (0, 255, 0), 2)
                
                # Add text label
                text_pos = (int(pts[0][0][0]), int(pts[0][0][1]) - 10)
                cv2.putText(
                    annotated_frame, f"{text} ({prob:.2f})", text_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
            
            # Join the texts with proper spacing
            full_text = " ".join(texts)
            
            # If debug is enabled and text was found, print it
            if self.show_debug and full_text.strip():
                print(f"Detected raw text: {full_text[:150]}...")
            
            return full_text, annotated_frame
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return "", original_frame
    
    def _summarize_text(self, text, max_sentences=3):
        """Summarize text to extract most important points"""
        # Return text directly if it's short
        if len(text.strip()) < 100:
            return text
            
        # Tokenize into sentences
        try:
            sentences = sent_tokenize(text)
            if len(sentences) <= max_sentences:
                return text
                
            # Use TF-IDF for better sentence ranking
            vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')
            tfidf = vectorizer.fit_transform(sentences)
            
            # Use NMF for topic extraction
            nmf = NMF(n_components=1, random_state=42).fit(tfidf)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get important words
            topic_words = [feature_names[i] for i in nmf.components_[0].argsort()[:-10:-1]]
            
            # Score sentences by presence of important words
            scores = []
            for sentence in sentences:
                score = sum([1 for word in topic_words if word.lower() in sentence.lower()])
                scores.append(score)
                
            # Get top sentences
            ranked_sentences = sorted(((scores[i], i) for i in range(len(sentences))), 
                                    reverse=True)
            
            # Prepare summary using original sentence order
            selected_indices = sorted([idx for _, idx in ranked_sentences[:max_sentences]])
            summary = " ".join([sentences[i] for i in selected_indices])
            
            if self.show_debug:
                print(f"Summarized text: {summary}")
                
            return summary
            
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fall back to first few sentences
            sentences = text.split('.')
            return '. '.join(sentences[:max_sentences]) + '.'
    
    def _speak_text(self, text):
        """Convert text to speech"""
        if not text.strip():
            return False
            
        try:
            # Stop any currently playing audio
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Create a temporary filename based on text hash to avoid regenerating same audio
            text_hash = hash(text) % 100000
            output_file = f"audio_cache_{text_hash}.mp3"
            
            # Only generate audio if it doesn't exist
            if not os.path.exists(output_file):
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_file)
            
            # Play audio
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            if self.show_debug:
                print(f"Speaking text: {text[:100]}...")
                
            return True
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    def _text_difference(self, text1, text2):
        """Calculate how different two texts are (0-1 scale)"""
        if not text1 or not text2:
            return 1.0
            
        # Simple difference measure based on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        union = len(words1.union(words2))
        if union == 0:
            return 0
            
        intersection = len(words1.intersection(words2))
        return 1 - (intersection / union)
    
    def _convert_frame_to_pygame(self, frame):
        """Convert OpenCV frame to Pygame surface correctly"""
        if frame is None:
            # Create a black frame if no frame is available
            empty = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame = empty
        
        # Convert from BGR (OpenCV) to RGB (Pygame)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create the pygame surface directly
        surface = pygame.surfarray.make_surface(np.transpose(rgb_frame, (1, 0, 2)))
            
        return surface
    
    def _render_text(self, surface, text, position=(10, 10), max_width=None, color=(255, 255, 255)):
        """Render text with word wrapping"""
        if not text.strip():
            return 0
            
        if max_width is None:
            max_width = self.width - 20
            
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = self.font.render(test_line, True, color)
            
            if text_surface.get_width() < max_width:
                current_line.append(word)
            else:
                if current_line:  # Avoid empty lines
                    lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        total_height = 0
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, color)
            y_pos = position[1] + i * (self.font.get_height() + 2)
            surface.blit(text_surface, (position[0], y_pos))
            total_height = y_pos + text_surface.get_height() - position[1]
            
        return total_height
    
    def _render_info_overlay(self, surface):
        """Render performance metrics and debug info"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((220, 100))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (self.width - 230, 10))
        
        # Render FPS
        fps_text = self.small_font.render(f"FPS: {self.fps}", True, (255, 255, 255))
        surface.blit(fps_text, (self.width - 220, 15))
        
        # Render OCR status
        if self.reader is None:
            status_text = self.small_font.render("OCR: Initializing...", True, (255, 150, 50))
        else:
            status_text = self.small_font.render("OCR: Ready", True, (100, 255, 100))
        surface.blit(status_text, (self.width - 220, 35))
        
        # Render processing interval
        interval_text = self.small_font.render(f"Process interval: {self.processing_interval:.1f}s", True, (255, 255, 255))
        surface.blit(interval_text, (self.width - 220, 55))
        
        # Display shortcuts
        help_text = self.small_font.render("Press 'F': Faster, 'S': Slower", True, (200, 200, 200))
        surface.blit(help_text, (self.width - 220, 75))
    
    def _render_text_overlay(self, surface):
        """Render the detected text overlay"""
        if not self.current_summary:
            return
            
        # Create semi-transparent overlay
        height = min(200, self.height // 3)
        overlay = pygame.Surface((self.width, height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, self.height - height))
        
        # Render summary text
        self._render_text(
            surface, 
            self.current_summary, 
            position=(10, self.height - height + 10),
            max_width=self.width - 20,
            color=(255, 255, 255)
        )
    
    def start(self):
        """Start the reading assistant"""
        if self.is_running:
            print("Reading assistant is already running")
            return
            
        self.is_running = True
        
        # Wait for OCR to initialize
        self.wait_for_ocr_init()
        
        # Initialize camera
        if not self.initialize_camera():
            self.is_running = False
            return
        
        # Start worker threads
        threading.Thread(target=self.capture_frames, daemon=True).start()
        threading.Thread(target=self.process_frames, daemon=True).start()
        threading.Thread(target=self.process_text, daemon=True).start()
        
        print("Reading assistant started. Press ESC to quit.")
        
        clock = pygame.time.Clock()
        try:
            while self.is_running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.is_running = False
                        elif event.key == pygame.K_f:  # Faster processing
                            self.processing_interval = max(0.2, self.processing_interval - 0.2)
                            print(f"Processing interval: {self.processing_interval:.1f}s")
                        elif event.key == pygame.K_s:  # Slower processing
                            self.processing_interval = min(3.0, self.processing_interval + 0.2)
                            print(f"Processing interval: {self.processing_interval:.1f}s")
                
                # Clear screen
                self.screen.fill((0, 0, 0))
                
                # Get latest processed frame if available
                if 'frame' in self.processed_results:
                    frame = self.processed_results['frame']
                    # Convert and display the frame
                    pygame_surface = self._convert_frame_to_pygame(frame)
                    self.screen.blit(pygame_surface, (0, 0))
                else:
                    # Capture and display camera feed even without processing
                    ret, frame = self.camera.read()
                    if ret:
                        pygame_surface = self._convert_frame_to_pygame(frame)
                        self.screen.blit(pygame_surface, (0, 0))
                
                # Render text overlay if we have summarized text
                self._render_text_overlay(self.screen)
                
                # Render debug information
                if self.show_debug:
                    self._render_info_overlay(self.screen)
                
                # Update display
                pygame.display.flip()
                
                # Control frame rate
                clock.tick(30)
                
        finally:
            self.stop()
    
    def stop(self):
        """Stop the reading assistant"""
        self.is_running = False
        
        # Wait for threads to finish
        time.sleep(0.5)
        
        # Release resources
        if self.camera is not None:
            self.camera.release()
            
        # Clean up pygame
        pygame.quit()
        
        # Remove temporary audio files
        for file in os.listdir():
            if file.startswith("audio_cache_") and file.endswith(".mp3"):
                try:
                    os.remove(file)
                except:
                    pass
        
        print("Reading assistant stopped.")

if __name__ == "__main__":
    print("Starting Optimized Real-time Reading Assistant...")
    
    try:
        assistant = OptimizedReadingAssistant()
        assistant.start()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your camera is connected and functioning")
        print("2. Ensure you have sufficient lighting for text recognition")
        print("3. Check that all required packages are installed")
        input("\nPress Enter to exit...")


#v0.4........................................................................................

# import cv2
# import numpy as np
# import threading
# import queue
# import time
# import os
# import pygame
# from gtts import gTTS
# import easyocr
# import nltk
# import torch

# # Ensure necessary NLTK data is downloaded
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt', quiet=True)

# class OptimizedReadingAssistant:
#     def __init__(self):
#         # Core components
#         self.camera = None
#         self.is_running = False
#         self.frame_queue = queue.Queue(maxsize=2)  # Limit frame queue size
#         self.text_queue = queue.Queue()
#         self.processed_results = {}  # Store processed results
        
#         # Timing control
#         self.processing_interval = 1.0  # Process frames every second
#         self.last_capture_time = 0
#         self.fps_counter = 0
#         self.fps_timer = time.time()
#         self.fps = 0
        
#         # Display settings
#         self.width = 1280
#         self.height = 720
#         self.show_debug = True
        
#         # State tracking
#         self.current_text = ""
#         self.previous_text = ""
        
#         # CUDA check - updated for PyTorch 2.2.0
#         self.gpu_available = torch.cuda.is_available()
#         if self.gpu_available:
#             self.device = torch.device('cuda')
#             # Set default CUDA device
#             torch.cuda.set_device(0)
#         else:
#             self.device = torch.device('cpu')
        
#         # Initialize pygame for display and audio
#         pygame.init()
#         pygame.mixer.init()
#         self.screen = pygame.display.set_mode((self.width, self.height))
#         pygame.display.set_caption("GPU-Accelerated Reading Assistant - Press ESC to quit")
#         self.font = pygame.font.SysFont("Arial", 24)
#         self.small_font = pygame.font.SysFont("Arial", 16)
        
#         # Initialize OCR in a separate thread to not block startup
#         self.reader = None
#         threading.Thread(target=self._init_ocr, daemon=True).start()
        
#     def _init_ocr(self):
#         """Initialize OCR engine in background thread with GPU acceleration"""
#         print("Initializing EasyOCR engine...")
#         print(f"GPU available: {self.gpu_available}")
#         if self.gpu_available:
#             print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        
#         try:
#             # Use more explicit GPU configuration
#             if self.gpu_available:
#                 # For PyTorch 2.2.0, ensure CUDA device is properly selected
#                 with torch.cuda.device(0):
#                     self.reader = easyocr.Reader(['en'], gpu=True, detector=True, recognizer=True)
#             else:
#                 self.reader = easyocr.Reader(['en'], gpu=False)
#             print("EasyOCR initialized successfully!")
#         except Exception as e:
#             print(f"Error initializing EasyOCR: {e}")
#             print("Falling back to CPU mode")
#             self.reader = easyocr.Reader(['en'], gpu=False)
        
#     def wait_for_ocr_init(self):
#         """Wait for OCR initialization to complete"""
#         max_wait_time = 60  # Maximum wait time in seconds
#         start_time = time.time()
        
#         while self.reader is None:
#             elapsed = time.time() - start_time
#             if elapsed > max_wait_time:
#                 print("OCR initialization is taking too long. Check for errors.")
#                 break
            
#             print("Waiting for OCR engine to initialize...")
#             time.sleep(1)
    
#     def initialize_camera(self):
#         """Initialize the camera with optimal settings for text detection"""
#         try:
#             self.camera = cv2.VideoCapture(0)
#             if not self.camera.isOpened():
#                 print("Could not open primary camera. Trying alternative...")
#                 self.camera = cv2.VideoCapture(1)
#                 if not self.camera.isOpened():
#                     raise Exception("No camera available")
            
#             # Configure camera for optimal text detection
#             self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
#             self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
#             self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Enable auto exposure
#             try:
#                 self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus if available
#             except:
#                 print("Autofocus setting not supported on this camera")
            
#             # Warm up camera
#             for _ in range(5):
#                 ret, _ = self.camera.read()
#                 if not ret:
#                     print("Warning: Camera warm-up frame capture failed")
#                 time.sleep(0.1)
                
#             return True
#         except Exception as e:
#             print(f"Camera initialization error: {e}")
#             return False
    
#     def capture_frames(self):
#         """Continuously capture frames from camera"""
#         while self.is_running:
#             if self.camera is None or not self.camera.isOpened():
#                 print("Camera not available")
#                 time.sleep(1)
#                 continue
                
#             ret, frame = self.camera.read()
#             if not ret:
#                 print("Failed to capture frame")
#                 time.sleep(0.1)
#                 continue
            
#             # Update FPS counter
#             self.fps_counter += 1
#             if time.time() - self.fps_timer >= 1.0:
#                 self.fps = self.fps_counter
#                 self.fps_counter = 0
#                 self.fps_timer = time.time()
            
#             # Only queue a new frame if current time exceeds the interval
#             current_time = time.time()
#             if current_time - self.last_capture_time >= self.processing_interval:
#                 # Skip if queue is full (prevents backlog)
#                 if self.frame_queue.full():
#                     try:
#                         self.frame_queue.get_nowait()  # Remove old frame
#                     except queue.Empty:
#                         pass
                
#                 # Add new frame for processing - use high-quality copy for book text
#                 try:
#                     self.frame_queue.put_nowait(frame.copy())
#                     self.last_capture_time = current_time
#                 except queue.Full:
#                     pass  # Skip if still full
    
#     def process_frames(self):
#         """Process frames from queue and extract text"""
#         while self.is_running:
#             if self.reader is None:
#                 time.sleep(0.5)  # Wait for OCR to initialize
#                 continue
                
#             try:
#                 frame = self.frame_queue.get(timeout=0.5)
                
#                 # Preprocessing for better OCR results - optimized for book text
#                 processed_frame = self._preprocess_image(frame)
                
#                 # Extract text in this thread
#                 extracted_text, annotated_frame = self._extract_text(processed_frame, frame)
                
#                 # Update processed results
#                 if extracted_text.strip():
#                     self.processed_results = {
#                         'text': extracted_text,
#                         'frame': annotated_frame,
#                         'timestamp': time.time()
#                     }
                    
#                     # Only add to text queue if text is significant
#                     if len(extracted_text) > 5:
#                         self.text_queue.put(extracted_text)
                        
#                 self.frame_queue.task_done()
                
#             except queue.Empty:
#                 pass  # No frames to process
#             except Exception as e:
#                 print(f"Frame processing error: {e}")
#                 time.sleep(0.5)
    
#     def process_text(self):
#         """Process extracted text for reading aloud"""
#         while self.is_running:
#             try:
#                 text = self.text_queue.get(timeout=0.5)
                
#                 # Only process text that is significantly different from previous
#                 if self._text_difference(text, self.previous_text) > 0.3:
#                     # Update state
#                     self.current_text = text
                    
#                     # Don't summarize, read the full text
#                     if self.show_debug:
#                         print(f"Full extracted text: {text}")
                    
#                     # Speak the text if significantly different
#                     self._speak_text(text)
#                     self.previous_text = text
                
#                 self.text_queue.task_done()
                
#             except queue.Empty:
#                 pass  # No text to process
#             except Exception as e:
#                 print(f"Text processing error: {e}")
    
#     def _preprocess_image(self, frame):
#         """Preprocess image for better book text OCR results"""
#         try:
#             # Convert to grayscale
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
#             # Apply CLAHE for better contrast
#             clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#             enhanced = clahe.apply(gray)
            
#             # Apply very light gaussian blur to reduce noise without losing text detail
#             blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
#             # Adaptive thresholding for better text detection - optimized for book text
#             thresh = cv2.adaptiveThreshold(
#                 blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                 cv2.THRESH_BINARY, 15, 9
#             )
            
#             # Morphological operations to connect nearby text components
#             kernel = np.ones((1, 1), np.uint8)
#             thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
#             return thresh
#         except Exception as e:
#             print(f"Image preprocessing error: {e}")
#             return frame if frame is not None else np.zeros((self.height, self.width), dtype=np.uint8)
    
#     def _extract_text(self, processed_image, original_frame):
#         """Extract text from preprocessed image - optimized for complete text extraction"""
#         try:
#             # Define confidence threshold for OCR
#             confidence_threshold = 0.3  # Lower threshold to capture more text
            
#             # Process at full resolution for better text recognition
#             results = self.reader.readtext(
#                 processed_image,
#                 paragraph=True,  # Group text into paragraphs
#                 detail=1,
#                 adjust_contrast=0.7,
#                 width_ths=0.7,  # Allow wider text grouping
#                 height_ths=0.7,  # Allow taller text grouping
#                 x_ths=1.0,  # Allow more horizontal grouping for paragraphs
#                 y_ths=0.5   # Allow more vertical grouping for paragraphs
#             )
            
#             # Draw bounding boxes on the original frame
#             annotated_frame = original_frame.copy()
            
#             # Extract text and annotate the frame
#             texts = []
#             for (bbox, text, prob) in results:
#                 # Only include confident detections
#                 if prob >= confidence_threshold:
#                     # Append text
#                     texts.append(text)
                    
#                     # Convert bbox to integer points
#                     pts = np.array(bbox, np.int32)
#                     pts = pts.reshape((-1, 1, 2))
                    
#                     # Draw filled polygon with transparency
#                     overlay = annotated_frame.copy()
#                     cv2.fillPoly(overlay, [pts.reshape((-1, 2))], (0, 255, 0, 0.3))
                    
#                     # Add the overlay with transparency
#                     alpha = 0.2
#                     annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1-alpha, 0)
                    
#                     # Draw outline
#                     cv2.polylines(annotated_frame, [pts.reshape((-1, 2))], True, (0, 255, 0), 2)
                    
#                     # Add text label
#                     text_pos = (int(pts[0][0][0]), int(pts[0][0][1]) - 10)
#                     cv2.putText(
#                         annotated_frame, f"{prob:.2f}", text_pos,
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
#                     )
            
#             # Order texts by vertical position (top to bottom)
#             # This helps maintain reading order for paragraphs
#             texts_with_positions = []
#             for (bbox, text, prob) in results:
#                 if prob >= confidence_threshold:
#                     # Get Y position of top-left corner
#                     y_pos = bbox[0][1]
#                     texts_with_positions.append((y_pos, text))
            
#             # Sort by Y position
#             texts_with_positions.sort()
            
#             # Extract ordered texts
#             ordered_texts = [text for _, text in texts_with_positions]
            
#             # Join the texts with proper spacing
#             full_text = " ".join(ordered_texts)
            
#             # If debug is enabled and text was found, print it
#             if self.show_debug and full_text.strip():
#                 print(f"Detected text length: {len(full_text)} characters")
            
#             return full_text, annotated_frame
            
#         except Exception as e:
#             print(f"OCR Error: {e}")
#             return "", original_frame
    
#     def _speak_text(self, text):
#         """Convert text to speech"""
#         if not text.strip():
#             return False
            
#         try:
#             # Stop any currently playing audio
#             if pygame.mixer.music.get_busy():
#                 pygame.mixer.music.stop()
            
#             # Create a temporary filename based on text hash to avoid regenerating same audio
#             text_hash = hash(text) % 100000
#             output_file = f"audio_cache_{text_hash}.mp3"
            
#             # Only generate audio if it doesn't exist
#             if not os.path.exists(output_file):
#                 tts = gTTS(text=text, lang='en', slow=False)
#                 tts.save(output_file)
            
#             # Play audio
#             pygame.mixer.music.load(output_file)
#             pygame.mixer.music.play()
            
#             if self.show_debug:
#                 print(f"Speaking text: {text[:100]}...")
                
#             return True
            
#         except Exception as e:
#             print(f"TTS Error: {e}")
#             return False
    
#     def _text_difference(self, text1, text2):
#         """Calculate how different two texts are (0-1 scale)"""
#         if not text1 or not text2:
#             return 1.0
            
#         # Simple difference measure based on words
#         words1 = set(text1.lower().split())
#         words2 = set(text2.lower().split())
        
#         union = len(words1.union(words2))
#         if union == 0:
#             return 0
            
#         intersection = len(words1.intersection(words2))
#         return 1 - (intersection / union)
    
#     def _convert_frame_to_pygame(self, frame):
#         """Convert OpenCV frame to Pygame surface correctly"""
#         try:
#             if frame is None:
#                 # Create a black frame if no frame is available
#                 empty = np.zeros((self.height, self.width, 3), dtype=np.uint8)
#                 frame = empty
            
#             # Convert from BGR (OpenCV) to RGB (Pygame)
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
#             # Ensure dimensions match expected shape
#             if rgb_frame.shape[0] != self.height or rgb_frame.shape[1] != self.width:
#                 rgb_frame = cv2.resize(rgb_frame, (self.width, self.height))
            
#             # Create the pygame surface directly
#             surface = pygame.surfarray.make_surface(np.transpose(rgb_frame, (1, 0, 2)))
                
#             return surface
#         except Exception as e:
#             print(f"Frame conversion error: {e}")
#             # Return a blank surface as fallback
#             return pygame.Surface((self.width, self.height))
    
#     def _render_text(self, surface, text, position=(10, 10), max_width=None, color=(255, 255, 255)):
#         """Render text with word wrapping"""
#         if not text.strip():
#             return 0
            
#         if max_width is None:
#             max_width = self.width - 20
            
#         words = text.split()
#         lines = []
#         current_line = []
        
#         for word in words:
#             test_line = ' '.join(current_line + [word])
#             text_surface = self.font.render(test_line, True, color)
            
#             if text_surface.get_width() < max_width:
#                 current_line.append(word)
#             else:
#                 if current_line:  # Avoid empty lines
#                     lines.append(' '.join(current_line))
#                 current_line = [word]
                
#         if current_line:
#             lines.append(' '.join(current_line))
            
#         total_height = 0
#         for i, line in enumerate(lines):
#             text_surface = self.font.render(line, True, color)
#             y_pos = position[1] + i * (self.font.get_height() + 2)
#             surface.blit(text_surface, (position[0], y_pos))
#             total_height = y_pos + text_surface.get_height() - position[1]
            
#         return total_height
    
#     def _render_info_overlay(self, surface):
#         """Render performance metrics and debug info"""
#         # Create semi-transparent overlay
#         overlay = pygame.Surface((260, 130))
#         overlay.set_alpha(180)
#         overlay.fill((0, 0, 0))
#         surface.blit(overlay, (self.width - 270, 10))
        
#         # Render FPS
#         fps_text = self.small_font.render(f"FPS: {self.fps}", True, (255, 255, 255))
#         surface.blit(fps_text, (self.width - 260, 15))
        
#         # Render GPU status
#         gpu_status = "Enabled" if self.gpu_available else "Disabled"
#         gpu_color = (100, 255, 100) if self.gpu_available else (255, 150, 50)
#         gpu_text = self.small_font.render(f"GPU: {gpu_status}", True, gpu_color)
#         surface.blit(gpu_text, (self.width - 260, 35))
        
#         # Render OCR status
#         if self.reader is None:
#             status_text = self.small_font.render("OCR: Initializing...", True, (255, 150, 50))
#         else:
#             status_text = self.small_font.render("OCR: Ready", True, (100, 255, 100))
#         surface.blit(status_text, (self.width - 260, 55))
        
#         # Render processing interval
#         interval_text = self.small_font.render(f"Process interval: {self.processing_interval:.1f}s", True, (255, 255, 255))
#         surface.blit(interval_text, (self.width - 260, 75))
        
#         # Display shortcuts
#         help_text1 = self.small_font.render("Press 'F': Faster, 'S': Slower", True, (200, 200, 200))
#         surface.blit(help_text1, (self.width - 260, 95))
#         help_text2 = self.small_font.render("Press 'ESC': Quit", True, (200, 200, 200))
#         surface.blit(help_text2, (self.width - 260, 115))
    
#     def _render_text_overlay(self, surface):
#         """Render the complete detected text overlay"""
#         if not self.current_text:
#             return
            
#         # Create semi-transparent overlay
#         height = min(300, self.height // 2)  # Make text area larger for full text
#         overlay = pygame.Surface((self.width, height))
#         overlay.set_alpha(180)
#         overlay.fill((0, 0, 0))
#         surface.blit(overlay, (0, self.height - height))
        
#         # Render full text
#         self._render_text(
#             surface, 
#             self.current_text, 
#             position=(10, self.height - height + 10),
#             max_width=self.width - 20,
#             color=(255, 255, 255)
#         )
    
#     def start(self):
#         """Start the reading assistant"""
#         if self.is_running:
#             print("Reading assistant is already running")
#             return
            
#         self.is_running = True
        
#         # Wait for OCR to initialize
#         self.wait_for_ocr_init()
        
#         # Initialize camera
#         if not self.initialize_camera():
#             self.is_running = False
#             print("Failed to initialize camera")
#             return
        
#         # Start worker threads
#         threading.Thread(target=self.capture_frames, daemon=True).start()
#         threading.Thread(target=self.process_frames, daemon=True).start()
#         threading.Thread(target=self.process_text, daemon=True).start()
        
#         print("Reading assistant started. Press ESC to quit.")
        
#         clock = pygame.time.Clock()
#         try:
#             while self.is_running:
#                 # Handle events
#                 for event in pygame.event.get():
#                     if event.type == pygame.QUIT:
#                         self.is_running = False
#                     elif event.type == pygame.KEYDOWN:
#                         if event.key == pygame.K_ESCAPE:
#                             self.is_running = False
#                         elif event.key == pygame.K_f:  # Faster processing
#                             self.processing_interval = max(0.2, self.processing_interval - 0.2)
#                             print(f"Processing interval: {self.processing_interval:.1f}s")
#                         elif event.key == pygame.K_s:  # Slower processing
#                             self.processing_interval = min(3.0, self.processing_interval + 0.2)
#                             print(f"Processing interval: {self.processing_interval:.1f}s")
                
#                 # Clear screen
#                 self.screen.fill((0, 0, 0))
                
#                 # Get latest processed frame if available
#                 if 'frame' in self.processed_results:
#                     frame = self.processed_results['frame']
#                     # Convert and display the frame
#                     pygame_surface = self._convert_frame_to_pygame(frame)
#                     self.screen.blit(pygame_surface, (0, 0))
#                 else:
#                     # Capture and display camera feed even without processing
#                     ret, frame = self.camera.read()
#                     if ret:
#                         pygame_surface = self._convert_frame_to_pygame(frame)
#                         self.screen.blit(pygame_surface, (0, 0))
                
#                 # Render text overlay if we have text
#                 self._render_text_overlay(self.screen)
                
#                 # Render debug information
#                 if self.show_debug:
#                     self._render_info_overlay(self.screen)
                
#                 # Update display
#                 pygame.display.flip()
                
#                 # Control frame rate
#                 clock.tick(30)
                
#         except Exception as e:
#             print(f"Main loop error: {e}")
#         finally:
#             self.stop()
    
#     def stop(self):
#         """Stop the reading assistant"""
#         self.is_running = False
        
#         # Wait for threads to finish
#         time.sleep(0.5)
        
#         # Release resources
#         if self.camera is not None:
#             self.camera.release()
            
#         # Clean up pygame
#         pygame.quit()
        
#         # Remove temporary audio files
#         for file in os.listdir():
#             if file.startswith("audio_cache_") and file.endswith(".mp3"):
#                 try:
#                     os.remove(file)
#                 except:
#                     pass
        
#         print("Reading assistant stopped.")

# if __name__ == "__main__":
#     print("Starting GPU-Accelerated Reading Assistant...")
#     print(f"PyTorch version: {torch.__version__}")
#     print(f"CUDA available: {torch.cuda.is_available()}")
    
#     if torch.cuda.is_available():
#         print(f"Number of GPU devices: {torch.cuda.device_count()}")
#         print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        
#         # Check CUDA memory
#         try:
#             print(f"Total GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
#             print(f"Available GPU memory: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
#         except:
#             print("Could not retrieve GPU memory information")
    
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#     print('Using device:', device)
    
#     try:
#         assistant = OptimizedReadingAssistant()
#         assistant.start()
#     except KeyboardInterrupt:
#         print("\nProgram interrupted by user.")
#     except Exception as e:
#         print(f"Error: {e}")
#         print("\nTroubleshooting tips:")
#         print("1. Make sure your camera is connected and functioning")
#         print("2. Ensure you have sufficient lighting for text recognition")
#         print("3. Check that all required packages are installed:")
#         print("   - opencv-python")
#         print("   - numpy")
#         print("   - pygame")
#         print("   - gtts")
#         print("   - easyocr")
#         print("   - nltk")
#         print("   - torch")
#         print("4. If CUDA is not being used, check your CUDA installation")
#         print("5. Try running with --verbose flag for more detailed error messages")
#         input("\nPress Enter to exit...")