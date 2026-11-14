#!/usr/bin/env python
"""Inference Pipeline for RuangIsyarat - MediaPipe + Model Inference."""

import cv2
import numpy as np
from typing import Optional, Tuple

# Try to import MediaPipe
try:
    import mediapipe as mp
    MP_AVAILABLE = True
    _mp_hands = mp.solutions.hands
    _mp_drawing = mp.solutions.drawing_utils
except ImportError:
    MP_AVAILABLE = False
    _mp_hands = None
    _mp_drawing = None


class InferencePipeline:
    """Hand gesture inference pipeline using MediaPipe and sklearn model."""
    
    def __init__(self, std_standar: str = "ASL", on_prediction=None):
        """
        Initialize inference pipeline.
        
        Args:
            std_standar: Standard bahasa isyarat (ASL, SIBI, BISINDO)
            on_prediction: Callback function when prediction changes
                signature: on_prediction(label: str, confidence: float)
        """
        self.std_standar = std_standar
        self.on_prediction = on_prediction
        self._running = False
        self._cap = None
        self.latest_result: Optional[Tuple[str, float]] = None
        
        # Model loading
        self._model = None
        self._label_encoder = None
        self._load_model()
        
        # MediaPipe Hands setup
        if MP_AVAILABLE and _mp_hands is not None:
            self._hands = _mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5,
            )
        else:
            self._hands = None
        
        # Gesture buffer for smoothing
        self._gesture_buffer = []
        self._buffer_size = 10
        
    def _load_model(self):
        """Load the trained model for the selected standard."""
        from pathlib import Path
        
        models_dir = Path(__file__).resolve().parents[1] / "models"
        model_path = models_dir / f"model_{self.std_standar.lower()}.pkl"
        
        if not model_path.exists():
            # Model not available - mark as None
            self._model = None
            self._label_encoder = None
            return
        
        try:
            import pickle
            with open(model_path, "rb") as f:
                data = pickle.load(f)
            
            # Handle different pickle formats
            if isinstance(data, dict):
                self._model = data.get("model")
                self._label_encoder = data.get("label_encoder", 
                    data.get("classes", None))
            else:
                self._model = data
                self._label_encoder = None
                
        except Exception as e:
            print(f"Error loading model: {e}")
            self._model = None
            self._label_encoder = None
    
    def process_frame(self, frame: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Process a single frame and return prediction.
        
        Args:
            frame: BGR image frame from camera
            
        Returns:
            Tuple of (label, confidence) or None if no hand detected
        """
        if not MP_AVAILABLE or self._hands is None or self._model is None:
            return None
        
        if not self._running:
            return None
        
        try:
            # Make a copy and flip
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            rgb_frame.flags.writeable = False
            results = self._hands.process(rgb_frame)
            rgb_frame.flags.writeable = True
            
            # No hand detected
            if not results.multi_hand_landmarks:
                # Reset buffer when no hand
                self._gesture_buffer = []
                self.latest_result = None
                return None
            
            # Process first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw landmarks on frame (optional - for debugging)
            # _mp_drawing.draw_landmarks(
            #     frame, hand_landmarks, _mp_hands.HAND_CONNECTIONS
            # )
            
            # Extract 21 landmarks (63 features: x, y, z for each)
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            
            # Normalize landmarks (relative to palm base - landmark 0)
            base_x = landmarks[0]
            base_y = landmarks[1]
            base_z = landmarks[2]
            
            normalized = []
            for i in range(0, 63, 3):
                normalized.extend([
                    round(landmarks[i] - base_x, 6),
                    round(landmarks[i+1] - base_y, 6),
                    round(landmarks[i+2] - base_z, 6),
                ])
            
            # Make prediction
            prediction = self._model.predict([normalized])[0]
            probabilities = self._model.predict_proba([normalized])[0]
            confidence = float(max(probabilities))
            
            # Get label name
            label = str(prediction)
            
            if self._label_encoder is not None:
                try:
                    label = str(
                        self._label_encoder.inverse_transform([prediction])[0]
                    )
                except Exception:
                    pass
            
            # Gesture buffer for smoothing
            self._gesture_buffer.append((label, confidence))
            if len(self._gesture_buffer) > self._buffer_size:
                self._gesture_buffer.pop(0)
            
            # Determine final label via majority vote in buffer
            final_label, final_confidence = self._smooth_gesture()
            self.latest_result = (final_label, final_confidence)
            
            return final_label, final_confidence
            
        except Exception as e:
            print(f"Error in inference pipeline: {e}")
            return None
    
    def _smooth_gesture(self) -> Tuple[str, float]:
        """Smooth gesture using buffer majority vote."""
        if not self._gesture_buffer:
            return "-", 0.0
        
        # Count occurrences of each label
        label_counts = {}
        total_confidence = 0.0
        
        for label, conf in self._gesture_buffer:
            label_counts[label] = label_counts.get(label, 0) + 1
            total_confidence += conf
        
        # Find most frequent label
        most_common_label = max(label_counts, key=label_counts.get)
        most_common_count = label_counts[most_common_label]
        
        # Calculate average confidence for this label
        label_confs = [conf for label, conf in self._gesture_buffer 
                       if label == most_common_label]
        avg_conf = sum(label_confs) / len(label_confs) if label_confs else 0.0
        
        # Only return if confidence threshold met
        if avg_conf > 0.5 and most_common_count >= 3:
            return most_common_label, avg_conf
        elif most_common_count >= 3:
            return most_common_label, avg_conf
        else:
            # Not enough consensus, return latest
            last_label, last_conf = self._gesture_buffer[-1]
            return last_label, last_conf
    
    def predict_from_landmarks(self, landmarks_63: list) -> Optional[Tuple[str, float]]:
        """
        Predict from pre-extracted landmarks.
        
        Args:
            landmarks_63: List of 63 normalized landmark features (x,y,z x21)
            
        Returns:
            Tuple of (label, confidence) or None
        """
        if self._model is None:
            return None
        
        try:
            import numpy as np
            import pickle
            
            # Convert to array and reshape
            features = np.array(landmarks_63).reshape(1, -1)
            
            # Predict
            prediction = self._model.predict(features)[0]
            probabilities = self._model.predict_proba(features)[0]
            confidence = float(max(probabilities))
            
            # Decode label
            label = str(prediction)
            if self._label_encoder is not None:
                try:
                    label = str(
                        self._label_encoder.inverse_transform([prediction])[0]
                    )
                except Exception:
                    pass
            
            return label, confidence
            
        except Exception as e:
            print(f"Error predicting from landmarks: {e}")
            return None
    
    def start(self):
        """Start the pipeline."""
        self._running = True
    
    def stop(self):
        """Stop the pipeline."""
        self._running = False
        if self._hands is not None:
            # MediaPipe resources are managed by context manager,
            # but we can force cleanup
            try:
                pass  # Hands object doesn't have explicit stop
            except:
                pass


def test_pipeline():
    """Simple test function for the pipeline."""
    import sys
    from PyQt6.QtWidgets import QApplication
    import numpy as np
    
    app = QApplication(sys.argv)
    
    pipeline = InferencePipeline(std_standar="ASL")
    
    # Open test camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Tidak dapat membuka kamera untuk testing")
        return
    
    print("Testing pipeline - menekan 'q' untuk keluar")
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Process frame
        result = pipeline.process_frame(frame)
        
        if result:
            label, confidence = result
            print(f"Prediksi: {label}, Keyakinan: {confidence:.3f}")
        
        # Show frame
        cv2.imshow("Pipeline Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pipeline.stop()


if __name__ == "__main__":
    test_pipeline()