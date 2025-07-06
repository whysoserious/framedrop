
import unittest
from unittest.mock import patch
from config import Config, ConfigError

class TestConfig(unittest.TestCase):

    @patch.dict('os.environ', {
        'BLUESKY_HANDLE': 'user',
        'BLUESKY_PASSWORD': 'pass',
        'VIDEO_PATH': '/vids/test.mp4',
        'SCHEDULE_TIMES': '08:00,20:00',
        'POST_TEXT': 'Hello',
        'ADD_TIMESTAMP': 'false'
    })
    def test_load_config_success(self):
        cfg = Config()
        self.assertEqual(cfg.bluesky_handle, 'user')
        self.assertEqual(cfg.bluesky_password, 'pass')
        self.assertEqual(cfg.video_path, '/vids/test.mp4')
        self.assertEqual(cfg.schedule_times, ['08:00', '20:00'])
        self.assertEqual(cfg.post_text, 'Hello')
        self.assertFalse(cfg.add_timestamp)

    @patch.dict('os.environ', {'BLUESKY_HANDLE': 'user', 'BLUESKY_PASSWORD': 'pass'})
    def test_validate_daemon_missing_video(self):
        cfg = Config()
        with self.assertRaises(ConfigError):
            cfg.validate_for_daemon()

    @patch.dict('os.environ', {})
    def test_validate_single_run_missing_credentials(self):
        cfg = Config()
        with self.assertRaises(ConfigError):
            cfg.validate_for_single_run()

if __name__ == '__main__':
    unittest.main()
