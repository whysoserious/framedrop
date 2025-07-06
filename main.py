import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="FrameDrop: Post random video frames to Bluesky.")
    parser.add_argument('--video', help='Path to the video file for a single run.')
    parser.add_argument('--text', help='Text to accompany the frame for a single run.')
    parser.add_argument('--timestamp', action='store_true', help='Include the frame timestamp in the post for a single run.')

    args = parser.parse_args()

    if args.video:
        # Single run mode
        print("Starting single run...")
        # Logic for single run will go here
    else:
        # Daemon mode
        print("Starting daemon mode...")
        # Logic for daemon mode will go here

if __name__ == "__main__":
    main()
