
import unittest
from unittest.mock import patch, MagicMock
from bluesky import BlueskyClient, BlueskyError
from atproto_client.models import blob_ref
from PIL import Image
import io

# Mock the entire atproto Client
@patch('bluesky.Client')
class TestBlueskyClient(unittest.TestCase):

    def test_login_success(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass', 1000)
        mock_instance.login.assert_called_once_with('user', 'pass')

    def test_login_failure(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.login.side_effect = Exception("Login failed")
        with self.assertRaises(BlueskyError):
            BlueskyClient('user', 'pass', 1000)

    def test_post_image_success(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass', 1000)
        
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
        client = BlueskyClient('user', 'pass', 1000)
        mock_instance.com.atproto.repo.upload_blob.return_value = None # Simulate upload failure

        with self.assertRaises(BlueskyError):
            with patch('builtins.open', unittest.mock.mock_open(read_data=b'img')):
                client.post_image('f.png', 't', 'a')

    def test_image_resizing(self, MockClient):
        mock_instance = MockClient.return_value
        client = BlueskyClient('user', 'pass', 1000) # Max size 1000 bytes

        # Create a dummy image that is larger than the max size
        img = Image.new('RGB', (200, 200), color = 'red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        large_image_data = buffer.getvalue()

        # Ensure the created image is actually larger
        self.assertTrue(len(large_image_data) > 1000)

        # Mock the blob upload
        mock_upload = MagicMock()
        mock_upload.blob = MagicMock(spec=blob_ref.BlobRef, cid='some_cid', mime_type='image/jpeg', size=900)
        mock_instance.com.atproto.repo.upload_blob.return_value = mock_upload
        mock_instance.get_current_time_iso.return_value = "2025-07-07T12:00:00.000Z"
        mock_instance.me.did = "did:plc:testuser"

        with patch('builtins.open', unittest.mock.mock_open(read_data=large_image_data)):
            client.post_image('large_image.jpg', 'Resized image', 'Alt text')

        # Check that upload_blob was called and the data passed to it is smaller
        mock_instance.com.atproto.repo.upload_blob.assert_called_once()
        uploaded_data = mock_instance.com.atproto.repo.upload_blob.call_args[0][0]
        self.assertTrue(len(uploaded_data) < len(large_image_data))
        self.assertTrue(len(uploaded_data) <= 1000)

if __name__ == '__main__':
    unittest.main()
