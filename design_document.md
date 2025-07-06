### Application Specification: FrameDrop

#### 1. Summary

"FrameDrop" is a Python application designed for automated posting to the Bluesky platform. Each post will include a randomly selected frame from a video file, user-provided text, and optionally the frame's timestamp. The application can operate in a one-time execution mode or as a persistent daemon process that publishes posts according to a schedule. The entire application is intended to run within a Docker environment.

#### 2. Core Functionalities

*   **Video Frame Extraction:** The application must be capable of opening video files (supported formats: .mp4, .avi, .mkv), reading their duration, randomly selecting a frame number, and then exporting that frame to an image format (PNG).
*   **Bluesky Publication:** The application will connect to the Bluesky API to publish a post consisting of:
    *   **Image:** The extracted video frame.
    *   **Text:** User-provided post content.
    *   **Alternative Text (Alt Text):** Automatically generated description, e.g., "Frame from [file name] at [timestamp]."
*   **Logging:** The application will output its operational logs to standard output, reporting successful publications or encountered errors.

#### 3. Architecture and Proposed Technologies

*   **Language:** Python 3.9+
*   **Video Handling:** `opencv-python-headless`
*   **Bluesky API Communication:** `atproto`
*   **CLI Argument Handling:** `argparse`
*   **Scheduler (for daemon mode):** `schedule`
*   **Dependency Management:** `requirements.txt` file.
*   **Configuration:** Bluesky login credentials and daemon mode configuration will be managed via environment variables.

#### 4. Operating Modes

**Mode 1: One-time Execution**

*   **Execution:** Script launched from the command line.
*   **Arguments:**
    *   `--video <path_to_file>` (required): Path to the video file.
    *   `--text <post_content>` (optional): Text to be published. If not provided, the application may use default text or omit it.
    *   `--timestamp` (optional, flag): If present, the frame's timestamp in `HH:MM:SS` format will be added to the post content.
*   **Example Usage:**
    ```bash
    python main.py --video "my_movie.mp4" --text "Random frame!" --timestamp
    ```

**Mode 2: Daemon Mode**

*   **Operation:** The script runs in a loop, publishing posts according to a schedule.
*   **Configuration (via environment variables):**
    *   `BLUESKY_HANDLE`: Bluesky user handle.
    *   `BLUESKY_PASSWORD`: Account password (or app key).
    *   `VIDEO_PATH`: Path to the video file from which frames will be randomly selected.
    *   `SCHEDULE_TIMES`: List of publication times, comma-separated (e.g., "10:00,18:30").
    *   `POST_TEXT`: Default post text.
*   **Error Handling:** In case of an error (e.g., network issues), the application will log the error and continue operation, waiting for the next scheduled post.

#### 5. Docker

*   The application will be packaged into a Docker image. The `Dockerfile` will be based on the `python:3.11-slim` image, install dependencies, and set `main.py` as the default entry point, running in daemon mode. One-time execution mode can be initiated by overriding the `docker run` command.
