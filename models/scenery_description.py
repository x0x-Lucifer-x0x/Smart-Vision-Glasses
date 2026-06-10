



#v - 2 #########################################################


    from typing import Dict, List, Optional, Tuple, Union, Any
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import numpy as np
    import time
    import os
    from dataclasses import dataclass
    from transformers import (
        DPTForDepthEstimation,
        DPTFeatureExtractor,
        DetrForObjectDetection,
        DetrImageProcessor,
        BlipProcessor,
        BlipForConditionalGeneration,
        ViTForImageClassification,
        ViTFeatureExtractor
    )

    from PIL import Image
    import cv2
    import warnings
    from pathlib import Path
    import logging
    import sys
    from concurrent.futures import ThreadPoolExecutor
    from contextlib import contextmanager
    import pyttsx3
    from threading import Thread, Lock, Event



    # Suppress TensorFlow logs
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



    # # Load emotion detection model
    # emotion_model.load_weights("src\\model.h5")
    # emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


    face_cascade = cv2.CascadeClassifier('src\\haarcascade_frontalface_default.xml')
    previous_emotion = None
    emotion_lock = Lock()


    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    @dataclass
    class NetworkOutput:
        """Type-safe container for network outputs"""
        scene_classification: torch.Tensor
        scene_change_probability: torch.Tensor
        scene_dynamics: torch.Tensor

    class AudioManager:
        def __init__(self):
            """Initialize text-to-speech engine"""
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.lock = Lock()
            self.speaking_thread = None
            self._stop_event = Event()
        
        def speak_async(self, text: str) -> None:
            """Speak text asynchronously but ensure it's thread-safe."""
            if self._stop_event.is_set():
                return
                
            def speak_text():
                with self.lock:
                    if not self._stop_event.is_set():
                        self.engine.say(text)
                        self.engine.runAndWait()
            
            if self.speaking_thread and self.speaking_thread.is_alive():
                self.speaking_thread.join(timeout=0.1)
            
            self.speaking_thread = Thread(target=speak_text)
            self.speaking_thread.daemon = True
            self.speaking_thread.start()
        
        def stop(self):
            """Stop the audio manager"""
            self._stop_event.set()
            if self.speaking_thread and self.speaking_thread.is_alive():
                self.speaking_thread.join(timeout=1.0)

    class SceneUnderstandingNetwork(nn.Module):
        def __init__(self, input_size: int = 768, num_classes: int = 50):
            super().__init__()
            self.input_size = input_size
            self.num_classes = num_classes
            
            # Feature extraction layers
            self.fc1 = nn.Linear(input_size, 512)
            self.dropout1 = nn.Dropout(0.3)
            self.fc2 = nn.Linear(512, 256)
            self.dropout2 = nn.Dropout(0.3)
            
            # Task-specific layers
            self.scene_classifier = nn.Linear(256, num_classes)
            self.change_detector = nn.Linear(256, 2)
            self.dynamics_predictor = nn.Linear(256, 5)
            
            self._initialize_weights()
        
        def _initialize_weights(self):
            for m in [self.fc1, self.fc2, self.scene_classifier, self.change_detector, self.dynamics_predictor]:
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)
        
        def forward(self, x: torch.Tensor) -> NetworkOutput:
            x = F.relu(self.fc1(x))
            x = self.dropout1(x)
            x = F.relu(self.fc2(x))
            x = self.dropout2(x)
            
            return NetworkOutput(
                scene_classification=self.scene_classifier(x),
                scene_change_probability=F.softmax(self.change_detector(x), dim=1),
                scene_dynamics=self.dynamics_predictor(x)
            )

    class AdvancedSceneAnalyzer:
        def __init__(self, model_cache_dir: Optional[Path] = None):
            """Initialize the scene analyzer"""
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self.device}")
            
            # Initialize components
            self.model_cache_dir = model_cache_dir
            self.audio_manager = AudioManager()
            self._executor = ThreadPoolExecutor(max_workers=2)
            self._stop_event = Event()
            
            # Initialize models
            self._load_models()
            
            # Initialize context memory
            self.context_memory = {
                'previous_features': None,
                'scene_history': [],
                'dynamics_history': [],
                'last_description_time': 0
            }
            
            self.scene_change_threshold = 0.7

        def _load_models(self):
            """Load all required models"""
            try:
                # Suppress warnings during model loading
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    
                    kwargs = {}
                    if self.model_cache_dir:
                        kwargs['cache_dir'] = self.model_cache_dir
                    
                    # Load depth estimation model
                    self.depth_model = DPTForDepthEstimation.from_pretrained(
                        "Intel/dpt-large", **kwargs
                    ).to(self.device)
                    self.depth_feature_extractor = DPTFeatureExtractor.from_pretrained(
                        "Intel/dpt-large", **kwargs
                    )
                    
                    # Load object detection model
                    self.object_detector = DetrForObjectDetection.from_pretrained(
                        "facebook/detr-resnet-50", **kwargs
                    ).to(self.device)
                    self.object_processor = DetrImageProcessor.from_pretrained(
                        "facebook/detr-resnet-50", **kwargs
                    )
                    
                    # Load caption generation model
                    self.caption_model = BlipForConditionalGeneration.from_pretrained(
                        "Salesforce/blip-image-captioning-large", **kwargs
                    ).to(self.device)
                    self.caption_processor = BlipProcessor.from_pretrained(
                        "Salesforce/blip-image-captioning-large", **kwargs
                    )
                    
                    # Load vision transformer model
                    self.vision_transformer = ViTForImageClassification.from_pretrained(
                        "google/vit-base-patch16-224", **kwargs
                    ).to(self.device)
                    self.feature_extractor = ViTFeatureExtractor.from_pretrained(
                        "google/vit-base-patch16-224", **kwargs
                    )
                    
                    # Initialize scene understanding network
                    self.scene_understanding = SceneUnderstandingNetwork().to(self.device)
                    self.scene_understanding.eval()
                    
                    logger.info("All models loaded successfully")
                    
            except Exception as e:
                logger.error(f"Failed to load models: {str(e)}")
                raise
        
        def extract_features(self, frame: np.ndarray) -> torch.Tensor:
            """Extract features from input frame"""
            if not isinstance(frame, np.ndarray):
                raise ValueError("Input frame must be a numpy array")
            
            # Convert BGR to RGB and to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Extract features using vision transformer
            inputs = self.feature_extractor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.vision_transformer(**inputs, output_hidden_states=True)
                features = outputs.hidden_states[-1][:, 0]  # Use CLS token
            
            return features.squeeze().cpu()

        def analyze_scene_dynamics(self, current_features: torch.Tensor) -> Tuple[bool, Optional[np.ndarray]]:
            """Analyze scene dynamics"""
            try:
                if self.context_memory['previous_features'] is not None:
                    feature_diff = torch.abs(
                        current_features - self.context_memory['previous_features']
                    )
                    
                    with torch.no_grad():
                        network_output = self.scene_understanding(
                            feature_diff.unsqueeze(0).to(self.device)
                        )
                    
                    scene_change_prob = network_output.scene_change_probability[0][1].cpu()
                    scene_dynamics = network_output.scene_dynamics.cpu()
                    
                    scene_changed = scene_change_prob > self.scene_change_threshold
                    
                    self.context_memory['scene_history'].append({
                        'changed': bool(scene_changed),
                        'dynamics': scene_dynamics.numpy()
                    })
                    
                    if len(self.context_memory['scene_history']) > 10:
                        self.context_memory['scene_history'].pop(0)
                    
                    return scene_changed, scene_dynamics.numpy()
                
                self.context_memory['previous_features'] = current_features
                return False, None
                
            except Exception as e:
                logger.error(f"Scene dynamics analysis failed: {str(e)}")
                raise

        def generate_intelligent_description(self, frame: np.ndarray, min_time_between_descriptions: float = 2.0) -> Optional[str]:
            """Generate scene description with timing control"""
            try:
                current_time = time.time()
                time_since_last = current_time - self.context_memory['last_description_time']
                
                if time_since_last < min_time_between_descriptions:
                    return None
                
                current_features = self.extract_features(frame)
                scene_changed, dynamics = self.analyze_scene_dynamics(current_features)
                
                if scene_changed:
                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    inputs = self.caption_processor(
                        images=pil_image, return_tensors="pt"
                    ).to(self.device)
                    
                    with torch.no_grad():
                        captions = self.caption_model.generate(**inputs)
                        description = self.caption_processor.decode(
                            captions[0], skip_special_tokens=True
                        )
                    
                    self.context_memory['last_description_time'] = current_time
                    return description
                
                return None
                
            except Exception as e:
                logger.error(f"Description generation failed: {str(e)}")
                return None

        def stop(self):
            """Stop the scene analyzer"""
            self._stop_event.set()
            self.audio_manager.stop()
            self._executor.shutdown(wait=False)

    def main():
        """Main function"""
        analyzer = None
        video_capture = None
        
        try:
            analyzer = AdvancedSceneAnalyzer()
            video_capture = cv2.VideoCapture(0)  # Try default camera first
            
            if not video_capture.isOpened():
                video_capture = cv2.VideoCapture(1)  # Try alternative camera
                if not video_capture.isOpened():
                    logger.error("Failed to open video capture")
                    return
            
            logger.info("Starting video capture...")
            
            cv2.namedWindow("Scene Analyzer", cv2.WINDOW_NORMAL)
            font = cv2.FONT_HERSHEY_DUPLEX
            
            while not (analyzer._stop_event.is_set() if analyzer else True):
                ret, frame = video_capture.read()
                if not ret:
                    logger.warning("Failed to capture frame")
                    break

            # Detect emotion in frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

                for (x, y, w, h) in faces:
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (48, 48))
                    face = face.astype("float") / 255.0
                    face = img_to_array(face)
                    face = np.expand_dims(face, axis=0)

                    preds = emotion_model.predict(face, verbose=0)[0]
                    emotion = emotion_labels[np.argmax(preds)]

                    # 🔴 Draw red rectangle around face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    # 🏷️ Put emotion label on top of the rectangle
                    cv2.putText(frame, emotion, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.9, (0, 0, 255), 2)

                    # 🗣️ Speak emotion if it's Angry or Fear and changed
                    with emotion_lock:
                        if emotion in ["Angry", "Fear"] and emotion != previous_emotion:
                            analyzer.audio_manager.speak_async(f"The person looks {emotion.lower()}")
                            previous_emotion = emotion
                        elif emotion not in ["Angry", "Fear"]:
                            previous_emotion = None  # Reset

                
                description = analyzer.generate_intelligent_description(
                    frame, min_time_between_descriptions=2.0
                )
                
                if description:
                    logger.info(f"Scene Change Detected: {description}")
                    
                    overlay = frame.copy()
                    cv2.rectangle(
                        overlay, (10, 10), (frame.shape[1]-10, 70), (0, 0, 0), -1
                    )
                    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                    
                    text_size = cv2.getTextSize(description, font, 1, 2)[0]
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    cv2.putText(
                        frame, description, (text_x, 50), font, 1, (255, 255, 255),
                        2, cv2.LINE_AA
                    )
                    
                    analyzer.audio_manager.speak_async(description)
                
                cv2.imshow("Scene Analyzer", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except Exception as e:
            logger.error(f"Error during video processing: {str(e)}")
        
        finally:
            if analyzer:
                analyzer.stop()
            if video_capture:
                video_capture.release()
            cv2.destroyAllWindows()
            logger.info("Video capture stopped and resources released")

        import main
        main.main()

    if __name__ == "__main__":
        main()