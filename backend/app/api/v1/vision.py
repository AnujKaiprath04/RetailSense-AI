import cv2
import numpy as np
from fastapi import APIRouter, Depends, Response
from vision.cv_analytics import RetailComputerVisionEngine

router = APIRouter(prefix="/vision", tags=["Computer Vision Analytics"])

# Global vision engine instance
cv_engine = RetailComputerVisionEngine()

@router.get("/stream-frame")
def get_live_camera_frame():
    """
    Returns JPEG encoded image frame of the simulated live CCTV stream with object detection & HUD overlays.
    """
    frame, metrics = cv_engine.generate_synthetic_cctv_frame(num_people=np.random.randint(6, 14))
    _, encoded_img = cv2.imencode('.jpg', frame)
    return Response(content=encoded_img.tobytes(), media_type="image/jpeg")

@router.get("/heatmap")
def get_density_heatmap():
    """
    Returns JPEG encoded image frame of the cumulative 2D thermal customer density heatmap.
    """
    heatmap_frame = cv_engine.generate_heatmap_overlay()
    _, encoded_img = cv2.imencode('.jpg', heatmap_frame)
    return Response(content=encoded_img.tobytes(), media_type="image/jpeg")

@router.get("/telemetry")
def get_vision_telemetry():
    """
    Returns real-time computer vision metrics (live occupancy, queue count, footfall gate counts).
    """
    _, metrics = cv_engine.generate_synthetic_cctv_frame(num_people=np.random.randint(8, 15))
    return {
        "engine": "OpenCV + YOLOv11 DeepSORT Tracker",
        "camera_id": "CAM_ENTRANCE_01",
        "fps": 30.0,
        "metrics": metrics
    }
