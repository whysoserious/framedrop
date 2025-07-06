import argparse
import os
import sys
import datetime
import schedule
import time

from config import Config, ConfigError
from video import extract_random_frame, VideoError
from bluesky import BlueskyClient, BlueskyError

def run_single_post(video_path, text, include_timestamp):
    """Runs the logic for a single post."""
    try:
        print(f"Starting single run for video: {video_path}")
        cfg = Config()
        cfg.validate_for_single_run()

        frame_path, timestamp = extract_random_frame(video_path)
        print(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")

        post_text = text
        if include_timestamp:
            time_str = str(datetime.timedelta(seconds=int(timestamp)))
            post_text = f"{text} [{time_str}]" if text else f"[{time_str}]"

        alt_text = f"A frame from {os.path.basename(video_path)} at {timestamp:.2f} seconds."

        client = BlueskyClient(cfg.bluesky_handle, cfg.bluesky_password)
        client.post_image(frame_path, post_text, alt_text)

    except (ConfigError, VideoError, BlueskyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.remove(frame_path)

def run_scheduled_post(cfg):
    """The main job for the daemon mode."""
    try:
        print("Running scheduled post...")
        frame_path, timestamp = extract_random_frame(cfg.video_path)
        print(f"Successfully extracted frame to: {frame_path} at {timestamp:.2f}s")

        post_text = cfg.post_text
        if cfg.add_timestamp:
            time_str = str(datetime.timedelta(seconds=int(timestamp)))
            post_text = f"{cfg.post_text} [{time_str}]" if cfg.post_text else f"[{time_str}]"

        alt_text = f"A frame from {os.path.basename(cfg.video_path)} at {timestamp:.2f} seconds."

        client = BlueskyClient(cfg.bluesky_handle, cfg.bluesky_password)
        client.post_image(frame_path, post_text, alt_text)

    except (VideoError, BlueskyError) as e:
        print(f"Scheduled post failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during scheduled post: {e}", file=sys.stderr)
    finally:
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.remove(frame_path)

def start_daemon_mode():
    """Starts the application in daemon mode."""
    print("Starting daemon mode...")
    try:
        cfg = Config()
        cfg.validate_for_daemon()

        for t in cfg.schedule_times:
            schedule.every().day.at(t.strip()).do(run_scheduled_post, cfg)
            print(f"Scheduled post at {t.strip()}")
        
        print("Scheduler started. Waiting for jobs...")
        while True:
            schedule.run_pending()
            time.sleep(1)

    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="FrameDrop: Post random video frames to Bluesky.")
    parser.add_argument('--video', help='Path to the video file for a single run.')
    parser.add_argument('--text', default="", help='Text to accompany the frame for a single run.')
    parser.add_argument('--timestamp', action='store_true', help='Include the frame timestamp in the post.')

    args = parser.parse_args()

    if args.video:
        run_single_post(args.video, args.text, args.timestamp)
    else:
        start_daemon_mode()

if __name__ == "__main__":
    main()