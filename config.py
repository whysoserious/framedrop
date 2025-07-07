
import os

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class Config:
    """Loads and validates configuration from environment variables."""
    def __init__(self):
        self.bluesky_handle = os.environ.get('BLUESKY_HANDLE')
        self.bluesky_password = os.environ.get('BLUESKY_PASSWORD')
        self.video_path = os.environ.get('VIDEO_PATH')
        self.schedule_times = os.environ.get('SCHEDULE_TIMES', '12:00').split(',')
        self.post_text = os.environ.get('POST_TEXT', '')
        self.add_timestamp = os.environ.get('ADD_TIMESTAMP', 'true').lower() == 'true'
        self.bluesky_max_upload_size = int(os.environ.get('BLUESKY_MAX_UPLOAD_SIZE', 900 * 1024))

    def validate_for_daemon(self):
        """Validate required configuration for daemon mode."""
        if not self.bluesky_handle or not self.bluesky_password:
            raise ConfigError("BLUESKY_HANDLE and BLUESKY_PASSWORD must be set for daemon mode.")
        if not self.video_path:
            raise ConfigError("VIDEO_PATH must be set for daemon mode.")

    def validate_for_single_run(self):
        """Validate required configuration for single run mode."""
        if not self.bluesky_handle or not self.bluesky_password:
            raise ConfigError("BLUESKY_HANDLE and BLUESKY_PASSWORD must be set as environment variables.")
