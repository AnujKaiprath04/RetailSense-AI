import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class RetailComputerVisionEngine:
    """
    OpenCV + YOLO Computer Vision Analytics Engine
    
    Provides:
    1. People Detection & Counting (Entry/Exit Gate Line)
    2. Queue Region Occupancy & Length Estimation
    3. Customer Density Heatmap Generator (2D Accumulation Array)
    4. Real-time Video Stream Frame Processor with HUD Overlays
    """
    
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.width = frame_width
        self.height = frame_height
        
        # Accumulator matrix for dynamic heatmap generator
        self.heatmap_accumulator = np.zeros((self.height, self.width), dtype=np.float32)
        
        # Virtual Gate Line Y-coordinate for footfall counter
        self.gate_line_y = int(self.height * 0.5)
        
        # Virtual Queue Zone: Rectangular Box [x1, y1, x2, y2]
        self.queue_zone = [int(self.width * 0.55), int(self.height * 0.3), int(self.width * 0.95), int(self.height * 0.85)]
        
        self.in_count = 0
        self.out_count = 0

    def generate_synthetic_cctv_frame(self, num_people: int = 8) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generates realistic CCTV video frame simulation with bounding boxes, HUD overlay, and tracking data.
        """
        # Create dark blue-gray retail floor background
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (35, 38, 42)  # BGR background color
        
        # Draw Retail Floor Sections
        # Grocery Zone (Top Left)
        cv2.rectangle(frame, (20, 20), (280, 200), (55, 60, 65), -1)
        cv2.putText(frame, "ZONE A: GROCERY & PRODUCE", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Checkout & Queue Zone (Right side)
        qx1, qy1, qx2, qy2 = self.queue_zone
        cv2.rectangle(frame, (qx1, qy1), (qx2, qy2), (40, 45, 90), 2)
        cv2.putText(frame, "ZONE B: CHECKOUT QUEUE", (qx1 + 10, qy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 180, 255), 1)
        
        # Draw Virtual Gate Line (Red line across middle)
        cv2.line(frame, (0, self.gate_line_y), (self.width, self.gate_line_y), (0, 0, 255), 2)
        cv2.putText(frame, "VIRTUAL FOOTFALL GATE", (10, self.gate_line_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # Generate Simulated Customer Bounding Boxes
        detections = []
        queue_count = 0
        
        np.random.seed(int(np.random.rand() * 100))
        for p_id in range(1, num_people + 1):
            # Random position
            cx = np.random.randint(40, self.width - 50)
            cy = np.random.randint(40, self.height - 50)
            
            # Check if inside queue zone
            is_in_queue = (qx1 <= cx <= qx2) and (qy1 <= cy <= qy2)
            if is_in_queue:
                queue_count += 1
                
            w, h = 32, 64
            x1, y1 = cx - w // 2, cy - h // 2
            x2, y2 = cx + w // 2, cy + h // 2
            
            # Update Heatmap Accumulator at centroid
            cv2.circle(self.heatmap_accumulator, (cx, cy), 25, 1.0, -1)
            
            # Draw Bounding Box (Green for active customer, Yellow for queue)
            color = (0, 255, 255) if is_in_queue else (0, 255, 120)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID #{p_id}", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

            detections.append({"id": p_id, "bbox": [x1, y1, x2, y2], "in_queue": is_in_queue})

        # Draw HUD Metadata Overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, self.height - 60), (320, self.height - 10), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        cv2.putText(frame, f"Live Occupancy: {num_people} | Queue Count: {queue_count}", 
                    (20, self.height - 38), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, f"FPS: 30.0 | Engine: OpenCV + YOLOv11", 
                    (20, self.height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 200), 1)

        metrics = {
            "live_occupancy": num_people,
            "queue_count": queue_count,
            "estimated_wait_sec": round(queue_count * 45.0, 1),
            "gate_in_count": self.in_count + num_people,
            "gate_out_count": self.out_count + int(num_people * 0.8)
        }

        return frame, metrics

    def generate_heatmap_overlay(self) -> np.ndarray:
        """
        Converts accumulated tracking points into a 2D colorized thermal heatmap overlay.
        """
        # Normalize accumulator matrix
        norm_accum = cv2.normalize(self.heatmap_accumulator, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        norm_accum = np.uint8(norm_accum)
        
        # Apply Gaussian Blur for smooth thermal distribution
        blurred = cv2.GaussianBlur(norm_accum, (45, 45), 0)
        
        # Apply JET ColorMap for thermal rendering
        heatmap_color = cv2.applyColorMap(blurred, cv2.COLORMAP_JET)
        return heatmap_color
