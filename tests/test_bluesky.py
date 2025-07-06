
import unittest
from unittest.mock import patch, MagicMock
from bluesky import BlueskyClient, BlueskyError
from atproto_client.models import blob_ref

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
        mock_upload.blob = MagicMock(spec=blob_ref.BlobRef, cid='some_cid', mime_type='image/png', size=1234)
        mock_instance.com.atproto.repo.upload_blob.return_value = mock_upload
        mock_instance.get_current_time_iso.return_value = "2025-07-06T12:00:00.000Z"
        mock_instance.me.did = "did:plc:testuser"

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
