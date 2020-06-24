import os
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from pathlib import Path
from PIL import Image, ExifTags

logger = logging.getLogger(__name__)

class ImageOperations:
    """
    Image manipulations class
    """

    def __init__(self, client_uuid, image_file):
        self._client_uuid = client_uuid
        self._image_file = image_file


    def crop_image_single(self, cropper):
        """
        Crop single image
        """
        pil_image = Image.open(self._image_file)

        # Image rotation fixing
        if pil_image.format in ('JPEG','JPG'):
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif=dict(pil_image._getexif().items())
            if exif[orientation] == 3:
                pil_image=pil_image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                pil_image=pil_image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                pil_image=pil_image.rotate(90, expand=True)

        crop_format = (
            pil_image.width * cropper['x'] / cropper['image_width'],
            pil_image.height * cropper['y'] / cropper['image_height'],
            pil_image.width * (cropper['x'] + cropper['width']) / cropper['image_width'],
            pil_image.height * (cropper['y'] + cropper['height']) / cropper['image_height'],
        )
        cropped = pil_image.crop(crop_format)
        output_filename = '.'.join((str(uuid.uuid4()), pil_image.format.lower()))
        
        cropped_path = os.path.join(settings.PUBLIC_DIR, 'cropped')
        Path(cropped_path).mkdir(parents=True, exist_ok=True)
        
        output_path = os.path.join(cropped_path, output_filename)
        cropped.save(output_path)
        
        crop_uuid = str(cropper.get('uuid'))
        return {
            'crop_uuid': output_path
        }

    def crop_image_multiformat(self, crop_data):
        """
        Crop image for multiple formats
        """
        pil_image = Image.open(self._image_file)

        # Image rotation fixing
        if pil_image.format in ('JPEG','JPG'):
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif=dict(pil_image._getexif().items())
            if exif[orientation] == 3:
                pil_image=pil_image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                pil_image=pil_image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                pil_image=pil_image.rotate(90, expand=True)

        cropping_results = dict()
        for cropper in crop_data: 
            crop_format = (
                pil_image.width * cropper['x'] / cropper['image_width'],
                pil_image.height * cropper['y'] / cropper['image_height'],
                pil_image.width * (cropper['x'] + cropper['width']) / cropper['image_width'],
                pil_image.height * (cropper['y'] + cropper['height']) / cropper['image_height'],
            )
            cropped = pil_image.crop(crop_format)
            output_filename = '.'.join((str(uuid.uuid4()), pil_image.format.lower()))
            
            cropped_path = os.path.join(settings.PUBLIC_DIR, 'cropped')
            Path(cropped_path).mkdir(parents=True, exist_ok=True)
            
            output_path = os.path.join(cropped_path, output_filename)
            cropped.save(output_path)
            
            crop_uuid = str(cropper.get('uuid'))
            cropping_results[crop_uuid] = output_path
        
        return cropping_results