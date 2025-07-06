# FrameDrop

> A simple Python application for automatically posting random frames from video files to Bluesky.

FrameDrop is a tool that helps bring your Bluesky account to life by regularly publishing frames from your favorite movies or other video materials. The application can run in the background, sending posts at scheduled times, or be launched for a single, one-time post.

## Key Features

-   **Frame Randomization:** Selects a random moment from a given video file and exports it as an image.
-   **Bluesky Publication:** Automatically sends a post with the image and defined text.
-   **Two Operating Modes:**
    1.  **Daemon Mode:** Runs continuously and publishes posts according to a schedule.
    2.  **Single Run Mode:** Publishes one post and then exits.
-   **Flexible Configuration:** All settings (login credentials, schedule, paths) are managed via environment variables.
-   **Docker Ready:** The entire application is packaged into a Docker image, making it easy to deploy.

## Prerequisites

1.  **Docker:** You need to have Docker installed on your computer.
2.  **Bluesky Account:** You need an active account on the Bluesky platform.
3.  **Video File:** Prepare a video file (e.g., in `.mp4`, `.avi`, `.mkv` format) from which frames will be extracted.

## Installation and Configuration

### Step 1: Prepare Bluesky Login Credentials

For security reasons, **do not use your main account password**. Instead, generate a dedicated "app password."

1.  Log in to your account on [bsky.app](https://bsky.app).
2.  Go to **Settings**.
3.  In the **Advanced** section, find and click **App Passwords**.
4.  Click **Add App Password** to generate a new password. Give it a name, e.g., `FrameDrop`.
5.  **Copy the generated password** (it will be in `xxxx-xxxx-xxxx-xxxx` format) and save it in a secure place. You will need it in the next step.
6.  You will also need your **handle** (username), e.g., `yourname.bsky.social`.

### Step 2: Configure Environment Variables

The application is configured using environment variables. Create a file named `.env` in the main project folder and fill it in according to the pattern below:

```env
# --- Bluesky Login Credentials ---
# Your Bluesky handle (username)
BLUESKY_HANDLE=yourname.bsky.social
# App password generated in the previous step
BLUESKY_PASSWORD=xxxx-xxxx-xxxx-xxxx

# --- Daemon Mode Configuration ---
# Path to the video file INSIDE the Docker container
VIDEO_PATH=/app/videos/my_movie.mp4
# Publication times, comma-separated
SCHEDULE_TIMES=10:00,18:30
# Default post text
POST_TEXT=Frame of the day!  فريمدروب
# Whether to include the timestamp in the post (true/false)
ADD_TIMESTAMP=true
```

**Important:** The `VIDEO_PATH` refers to the file system *inside* the Docker container. In the next step, we will show you how to map your local video folder to this path.

### Step 3: Build the Docker Image

Open a terminal in the main project folder and execute the command:

```bash
docker build -t framedrop .
```

This command will build a Docker image named `framedrop` based on the `Dockerfile`.

## Running the Application

Make sure you have your `.env` file ready and a folder with your video file.

### Daemon Mode (recommended)

This mode runs the application in the background. It will publish posts at the times defined in `SCHEDULE_TIMES`.

Run the container using the command below. Remember to replace `/path/to/your/videos` with the actual path to the folder containing your video files on your computer.

```bash
docker run -d --env-file .env -v /path/to/your/videos:/app/videos --name framedrop-app framedrop
```

-   `-d`: Runs the container in "detached" mode (in the background).
-   `--env-file .env`: Loads environment variables from the `.env` file.
-   `-v /path/to/your/videos:/app/videos`: Maps your local video folder to the `/app/videos` folder inside the container.
-   `--name framedrop-app`: Assigns a friendly name to the container.

To view application logs:
`docker logs -f framedrop-app`

To stop the application:
`docker stop framedrop-app`

### Single Run Mode

If you want to publish only one frame, you can run the container by overriding the default command.

```bash
docker run --rm --env-file .env -v /path/to/your/videos:/app/videos framedrop \
  python main.py \
    --video /app/videos/another_movie.mp4 \
    --text "Special post!" \
    --timestamp
```

-   `--rm`: Automatically removes the container after it finishes.
-   After the image name (`framedrop`), we provide the new command to execute inside the container.

## Configuration Details (Environment Variables)

| Variable          | Description                                                                                      | Default   | Required      |
| ----------------- | ------------------------------------------------------------------------------------------------ | --------- | ------------- |
| `BLUESKY_HANDLE`  | Your Bluesky handle (username).                                                                  | -         | **Yes**       |
| `BLUESKY_PASSWORD`| The generated app password.                                                                      | -         | **Yes**       |
| `VIDEO_PATH`      | Path to the video file for daemon mode.                                                          | -         | For daemon mode |
| `SCHEDULE_TIMES`  | Publication times for daemon mode (`HH:MM` format, comma-separated).                             | `12:00`   | No            |
| `POST_TEXT`       | Default text to include in the post.                                                             | ""        | No            |
| `ADD_TIMESTAMP`   | Whether to add the frame timestamp to the post text (`true` or `false`).                         | `true`    | No            |

```