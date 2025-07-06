
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from video import extract_random_frame, VideoError

# Since we can't rely on cv2 in a bare environment, we mock it entirely.
# We create a fake VideoCapture object.
class MockVideoCapture:
    def __init__(self, path):
        self._is_opened = os.path.exists(path)
        self._frame_count = 100
        self._pos_msec = 5000

    def isOpened(self):
        return self._is_opened

    def get(self, prop_id):
        if prop_id == 7: # CAP_PROP_FRAME_COUNT
            return self._frame_count
        if prop_id == 0: # CAP_PROP_POS_MSEC
            return self._pos_msec
        return 0

    def set(self, prop_id, value):
        return True

    def read(self):
        return True, "fake_frame_data"

    def release(self):
        pass

@patch('video.cv2.VideoCapture', new=MockVideoCapture)
@patch('video.cv2.imwrite', return_value=True)
class TestVideo(unittest.TestCase):

    def setUp(self):
        self.video_path = 'tests/assets/test_video.mp4'
        # Ensure the dummy file exists
        os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
        with open(self.video_path, 'w') as f:
            f.write('dummy video')

    def tearDown(self):
        if os.path.exists(self.video_path):
            os.remove(self.video_path)

    def test_extract_random_frame_success(self, mock_imwrite):
        frame_path, timestamp = extract_random_frame(self.video_path)
        self.assertIsNotNone(frame_path)
        self.assertGreater(timestamp, 0)
        mock_imwrite.assert_called_once()
        # Verify that imwrite was called with a path in the temp directory and a .png extension
        self.assertTrue(frame_path.startswith(tempfile.gettempdir()))
        self.assertTrue(frame_path.endswith('.png'))

    def test_extract_frame_file_not_found(self, mock_imwrite):
        with self.assertRaises(VideoError):
            extract_random_frame('non_existent_file.mp4')

if __name__ == '__main__':
    unittest.main()
