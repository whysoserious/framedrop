
from atproto import Client
from atproto_client.models.app.bsky.feed import post as AppBskyFeedPost
from atproto_client.models.app.bsky.embed import images as AppBskyEmbedImages
from atproto_client.models import ids, ComAtprotoRepoCreateRecord, ComAtprotoRepoStrongRef
import os
from PIL import Image
import io

class BlueskyError(Exception):
    """Custom exception for Bluesky API errors."""
    pass

class BlueskyClient:
    def __init__(self, handle, password, max_upload_size):
        self.client = Client()
        self.handle = handle
        self.password = password
        self.max_upload_size = max_upload_size
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

            if len(img_data) > self.max_upload_size:
                img = Image.open(io.BytesIO(img_data))
                
                # Start with high quality and reduce until the size is acceptable
                quality = 95
                while quality > 10: # Don't go below a quality of 10
                    buffer = io.BytesIO()
                    # Preserve original format if possible, default to JPEG
                    img_format = img.format or 'JPEG'
                    img.save(buffer, format=img_format, quality=quality)
                    if buffer.tell() <= self.max_upload_size:
                        img_data = buffer.getvalue()
                        break
                    quality -= 5
                else:
                    # If the loop completes without breaking, try reducing image size
                    while img.width > 100 and img.height > 100:
                        img = img.resize((int(img.width * 0.9), int(img.height * 0.9)), Image.Resampling.LANCZOS)
                        buffer = io.BytesIO()
                        img.save(buffer, format=img.format or 'JPEG', quality=95)
                        if buffer.tell() <= self.max_upload_size:
                            img_data = buffer.getvalue()
                            break
                    else:
                        # If the image is still too large after resizing, raise an error
                        raise BlueskyError(f"Could not resize image to under {self.max_upload_size} bytes.")

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

