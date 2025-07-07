import argparse
import os
import sys
import datetime
import schedule
import time
import logging

from config import Config, ConfigError
from video import extract_random_frame, VideoError
from bluesky import BlueskyClient, BlueskyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_single_post(video_path, text, include_timestamp):
    """Runs the logic for a single post."""
    try:
        logging.info(f"Starting single run for video: {video_path}")
        cfg = Config()
        cfg.validate_for_single_run()

        frame_path, timestamp = extract_random_frame(video_path)
        logging.info(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")

        post_text = text
        if include_timestamp:
            time_str = str(datetime.timedelta(seconds=int(timestamp)))
            post_text = f"{text} [{time_str}]" if text else f"[{time_str}]"

        alt_text = f"A frame from {os.path.basename(video_path)} at {timestamp:.2f} seconds."

        client = BlueskyClient(cfg.bluesky_handle, cfg.bluesky_password, cfg.bluesky_max_upload_size)
        client.post_image(frame_path, post_text, alt_text)
        logging.info("Single run completed.")

    except (ConfigError, VideoError, BlueskyError) as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.remove(frame_path)

def run_scheduled_post(cfg):
    """The main job for the daemon mode."""
    try:
        logging.info("Running scheduled post...")
        frame_path, timestamp = extract_random_frame(cfg.video_path)
        logging.info(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")

        post_text = cfg.post_text
        if cfg.add_timestamp:
            time_str = str(datetime.timedelta(seconds=int(timestamp)))
            post_text = f"{cfg.post_text} [{time_str}]" if cfg.post_text else f"[{time_str}]"

        alt_text = f"A frame from {os.path.basename(cfg.video_path)} at {timestamp:.2f} seconds."

        client = BlueskyClient(cfg.bluesky_handle, cfg.bluesky_password, cfg.bluesky_max_upload_size)
        client.post_image(frame_path, post_text, alt_text)

    except (VideoError, BlueskyError) as e:
        logging.error(f"Scheduled post failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during scheduled post: {e}")
    finally:
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.remove(frame_path)

def start_daemon_mode():
    """Starts the application in daemon mode."""
    logging.info("Daemon mode started.")
    try:
        cfg = Config()
        cfg.validate_for_daemon()

        for t in cfg.schedule_times:
            schedule.every().day.at(t.strip()).do(run_scheduled_post, cfg)
            logging.info(f"Scheduled post at {t.strip()}")
        
        logging.info("Scheduler started. Waiting for jobs...")
        while True:
            schedule.run_pending()
            time.sleep(1)

    except ConfigError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    finally:
        logging.info("Daemon mode stopped.")

def main():
    logging.info("FrameDrop application started.")
    parser = argparse.ArgumentParser(description="FrameDrop: Post random video frames to Bluesky.")
    parser.add_argument('--video', help='Path to the video file for a single run.')
    parser.add_argument('--text', default="", help='Text to accompany the frame for a single run.')
    parser.add_argument('--timestamp', action='store_true', help='Include the frame timestamp in the post.')

    args = parser.parse_args()

    cfg = Config()
    logging.info("Loaded configuration:")
    logging.info(f"  BLUESKY_HANDLE: {cfg.bluesky_handle}")
    logging.info(f"  BLUESKY_PASSWORD: {'*' * len(cfg.bluesky_password) if cfg.bluesky_password else 'N/A'}") # Mask password
    logging.info(f"  VIDEO_PATH: {cfg.video_path}")
    logging.info(f"  SCHEDULE_TIMES: {', '.join(cfg.schedule_times)}")
    logging.info(f"  POST_TEXT: '{cfg.post_text}'")
    logging.info(f"  ADD_TIMESTAMP: {cfg.add_timestamp}")
    logging.info(f"  BLUESKY_MAX_UPLOAD_SIZE: {cfg.bluesky_max_upload_size} bytes")

    if args.video:
        run_single_post(args.video, args.text, args.timestamp)
    else:
        start_daemon_mode()

if __name__ == "__main__":
    main()