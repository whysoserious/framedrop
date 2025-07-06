
import cv2
import random
import os
import tempfile

class VideoError(Exception):
    """Custom exception for video processing errors."""
    pass

def extract_random_frame(video_path):
    """Extracts a random frame from a video file and saves it as a temporary image.

    Args:
        video_path (str): The path to the video file.

    Returns:
        tuple: A tuple containing the path to the saved frame image and its timestamp in seconds.
    
    Raises:
        VideoError: If the video cannot be opened, has no frames, or a frame cannot be read.
    """
    if not os.path.exists(video_path):
        raise VideoError(f"Video file not found at: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise VideoError(f"Could not open video file: {video_path}")

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise VideoError(f"Video file has no frames: {video_path}")

        random_frame_number = random.randint(0, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)

        success, frame = cap.read()
        if not success:
            raise VideoError("Failed to read frame from video.")

        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        timestamp_sec = timestamp_ms / 1000.0

        temp_dir = tempfile.gettempdir()
        frame_path = os.path.join(temp_dir, f"framedrop_{random.randint(1000, 9999)}.png")
        cv2.imwrite(frame_path, frame)

        return frame_path, timestamp_sec

    finally:
        cap.release()
