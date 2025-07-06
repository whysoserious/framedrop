This is a draft plan for a new application called __FrameRater__.

This application is intended to send a post to a Bluesky account, which includes a random frame from a given video file, specified content, and optionally the frame's timestamp.

Operating modes:
- One-time script execution will send a post to Bluesky. The post content can be provided from the command line. The script will randomly select a frame from the specified .avi video file.
- Daemon mode: the script runs continuously and sends posts at specified times. Propose how to implement this.

Both modes should run within a Docker image.

Programming language: Python.

Prepare detailed logs.
All code, all comments, and logs should be in English.
