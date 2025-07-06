
from atproto import Client
from atproto_client.models.app.bsky.feed import post as AppBskyFeedPost
from atproto_client.models.app.bsky.embed import images as AppBskyEmbedImages
from atproto_client.models import ids, ComAtprotoRepoCreateRecord, ComAtprotoRepoStrongRef
import os

class BlueskyError(Exception):
    """Custom exception for Bluesky API errors."""
    pass

class BlueskyClient:
    def __init__(self, handle, password):
        self.client = Client()
        self.handle = handle
        self.password = password
        self._login()

    def _login(self):
        try:
            self.client.login(self.handle, self.password)
        except Exception as e:
            raise BlueskyError(f"Failed to login to Bluesky: {e}")

    def post_image(self, image_path, post_text, alt_text):
        """Posts an image and text to Bluesky.

        Args:
            image_path (str): The path to the image file.
            post_text (str): The text of the post.
            alt_text (str): The alt text for the image.
        
        Raises:
            BlueskyError: If the post fails.
        """
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()

            upload = self.client.com.atproto.repo.upload_blob(img_data)
            if not upload:
                raise BlueskyError("Failed to upload image blob.")

            embed = AppBskyEmbedImages.Main(images=[AppBskyEmbedImages.Image(alt=alt_text, image=upload.blob)])
            
            self.client.com.atproto.repo.create_record(
                ComAtprotoRepoCreateRecord.Data(
                    repo=self.client.me.did,
                    collection=ids.AppBskyFeedPost,
                    record=AppBskyFeedPost.Record(
                        text=post_text, 
                        created_at=self.client.get_current_time_iso(), 
                        embed=embed
                    )
                )
            )
            print("Successfully posted to Bluesky!")
        except Exception as e:
            raise BlueskyError(f"An error occurred while posting to Bluesky: {e}")

