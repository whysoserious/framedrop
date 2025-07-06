
import unittest
from unittest.mock import patch, MagicMock
from bluesky import BlueskyClient, BlueskyError
from atproto import models # Import models

# Mock the entire atproto Client
@patch('bluesky.Client')
class TestBlueskyClient(unittest.TestCase):

    def test_login_success(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass')
        mock_instance.login.assert_called_once_with('user', 'pass')

    def test_login_failure(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.login.side_effect = Exception("Login failed")
        with self.assertRaises(BlueskyError):
            BlueskyClient('user', 'pass')

    def test_post_image_success(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass')
        
        # Mock the blob upload and record creation
        mock_upload = MagicMock()
        # Ensure mock_upload.blob is an instance of models.BlobRef
        mock_upload.blob = MagicMock(spec=models.BlobRef, cid='some_cid', mime_type='image/png', size=1234)
        mock_instance.com.atproto.repo.upload_blob.return_value = mock_upload

        with patch('builtins.open', unittest.mock.mock_open(read_data=b'img')):
            client.post_image('fake_path.png', 'Hello', 'Alt text')

        mock_instance.com.atproto.repo.upload_blob.assert_called_once()
        mock_instance.com.atproto.repo.create_record.assert_called_once()

    def test_post_image_upload_fails(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass')
        mock_instance.com.atproto.repo.upload_blob.return_value = None # Simulate upload failure

        with self.assertRaises(BlueskyError):
            with patch('builtins.open', unittest.mock.mock_open(read_data=b'img')):
                client.post_image('f.png', 't', 'a')

if __name__ == '__main__':
    unittest.main()
