import argparse
import os
import cv2
import random
import tempfile
import datetime
import schedule
import time
from atproto import Client, models

def extract_random_frame(video_path):
    """Extracts a random frame from a video file and saves it as a temporary image.

    Args:
        video_path (str): The path to the video file.

    Returns:
        tuple: A tuple containing the path to the saved frame image and its timestamp in seconds, or (None, None) if an error occurs.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file: {video_path}")
            return None, None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            print(f"Error: Video file has no frames: {video_path}")
            return None, None

        random_frame_number = random.randint(0, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)

        success, frame = cap.read()
        if not success:
            print("Error: Failed to read frame from video.")
            return None, None

        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        timestamp_sec = timestamp_ms / 1000.0

        temp_dir = tempfile.gettempdir()
        frame_path = os.path.join(temp_dir, "framedrop_frame.png")
        cv2.imwrite(frame_path, frame)

        cap.release()
        return frame_path, timestamp_sec

    except Exception as e:
        print(f"An error occurred during frame extraction: {e}")
        return None, None

def post_to_bluesky(image_path, post_text, alt_text):
    """Posts an image and text to Bluesky.

    Args:
        image_path (str): The path to the image file.
        post_text (str): The text of the post.
        alt_text (str): The alt text for the image.
    """
    try:
        client = Client()
        client.login(
            os.environ['BLUESKY_HANDLE'],
            os.environ['BLUESKY_PASSWORD']
        )

        with open(image_path, 'rb') as f:
            img_data = f.read()

        upload = client.com.atproto.repo.upload_blob(img_data)
        embed = models.ComAtprotoRepoStrongRef.Main(
            cid=upload.blob.cid,
            uri=client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Data(
                    repo=client.me.did,
                    collection=models.ids.AppBskyFeedPost,
                    record=models.AppBskyFeedPost.Main(text=post_text, created_at=client.get_current_time_iso(), embed=models.AppBskyEmbedImages.Main(images=[models.AppBskyEmbedImages.Image(alt=alt_text, image=upload.blob)]))                )
            ).uri
        )

        print("Successfully posted to Bluesky!")

    except Exception as e:
        print(f"An error occurred while posting to Bluesky: {e}")

def run_scheduled_post():
    """The main job for the daemon mode, controlled by environment variables."""
    print("Running scheduled post...")
    video_path = os.environ.get('VIDEO_PATH')
    if not video_path:
        print("Error: VIDEO_PATH environment variable not set.")
        return

    frame_path, timestamp = extract_random_frame(video_path)
    if frame_path:
        print(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")
        
        post_text = os.environ.get('POST_TEXT', '')
        if os.environ.get('ADD_TIMESTAMP', 'true').lower() == 'true':
            time_str = str(datetime.timedelta(seconds=int(timestamp)))
            post_text = f"{post_text} [{time_str}]"

        alt_text = f"A frame from the video {os.path.basename(video_path)} at {timestamp:.2f} seconds."

        post_to_bluesky(frame_path, post_text, alt_text)

        # Clean up the temporary file
        os.remove(frame_path)

def main():
    parser = argparse.ArgumentParser(description="FrameDrop: Post random video frames to Bluesky.")
    parser.add_argument('--video', help='Path to the video file for a single run.')
    parser.add_argument('--text', default="", help='Text to accompany the frame for a single run.')
    parser.add_argument('--timestamp', action='store_true', help='Include the frame timestamp in the post for a single run.')

    args = parser.parse_args()

    if args.video:
        # Single run mode
        print(f"Starting single run for video: {args.video}")
        frame_path, timestamp = extract_random_frame(args.video)
        if frame_path:
            print(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")
            
            post_text = args.text
            if args.timestamp:
                time_str = str(datetime.timedelta(seconds=int(timestamp)))
                post_text = f"{post_text} [{time_str}]"

            alt_text = f"A frame from the video {os.path.basename(args.video)} at {timestamp:.2f} seconds."

            post_to_bluesky(frame_path, post_text, alt_text)

            # Clean up the temporary file
            os.remove(frame_path)
    else:
        # Daemon mode
        print("Starting daemon mode...")
        schedule_times = os.environ.get('SCHEDULE_TIMES', '12:00').split(',')
        for t in schedule_times:
            schedule.every().day.at(t.strip()).do(run_scheduled_post)
            print(f"Scheduled post at {t.strip()}")

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
