import os
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from pathlib import Path
from PIL import Image, ExifTags, ImageOps

logger = logging.getLogger(__name__)

class ImageOperations:
    """
    Image manipulations class
    """

    def __init__(self, client_uuid, image_file):
        self._client_uuid = client_uuid
        self._image_file = image_file


    def _save_pil_image(self, pil_image:Image, filename:str, subdir:str):
        """
        pil_image: PIL.Image - image
        filename: str - the output filename
        subdir: str - a subdirectory in the SHARED directory that has mnemonic association with application or function like "resize", "crop", etc
        """

        image_path = os.path.join(settings.PUBLIC_DIR_SHARED, subdir)
        Path(image_path).mkdir(parents=True, exist_ok=True)
        
        # output_filename = '.'.join((str(uuid.uuid4()), image_format))
        output_path = os.path.join(image_path, filename)

        pil_image.save(output_path)

        image_path_public = Path(settings.PUBLIC_DIR) / subdir / filename
        return {
            'saved': output_path,
            'public': str(image_path_public)
        }

    def _fix_exif(self, pil_image:Image, image_format:str):
        # Fix pil image exif format
        img = ImageOps.exif_transpose(pil_image)
        return img

    def resize_image_single(self, resizer):
        """
            Resize single image
            :return dict: {
                'saved' -  file location in the filestem
                'public' -  file location in the filestem
            }
        """

        pil_image:Image = Image.open(self._image_file)
        image_format = pil_image.format.lower()
        # Fixing EXIF
        pil_image = self._fix_exif(pil_image, image_format)
        
        new_size = (int(resizer.get('width')), int(resizer.get('height')))
        pil_resized_image = pil_image.resize(new_size, Image.ANTIALIAS)
        filename = '.'.join(( str(uuid.uuid4()), image_format ))
        save_result = self._save_pil_image(pil_resized_image, filename, 'resizer')
        return save_result

    def crop_image_single(self, cropper):
        """
        Crop single image
        """
        
        pil_image:Image = Image.open(self._image_file)
        image_format = pil_image.format.lower()
        # Fixing EXIF
        pil_image = self._fix_exif(pil_image, image_format)

        crop_format = (
            pil_image.width * cropper['x'] / cropper['image_width'],
            pil_image.height * cropper['y'] / cropper['image_height'],
            pil_image.width * (cropper['x'] + cropper['width']) / cropper['image_width'],
            pil_image.height * (cropper['y'] + cropper['height']) / cropper['image_height'],
        )
        cropped = pil_image.crop(crop_format)
        
        cropped_path = os.path.join(settings.PUBLIC_DIR_SHARED, 'cropped')
        Path(cropped_path).mkdir(parents=True, exist_ok=True)
        
        output_filename = '.'.join((str(uuid.uuid4()), image_format))
        output_path = os.path.join(cropped_path, output_filename)
        cropped.save(output_path)
        
        croppped_path_public = Path(settings.PUBLIC_DIR) / 'cropped' / output_filename
        
        return {
            'url':  str(croppped_path_public)
        }

    def crop_image_multiformat(self, crop_data):
        """
        Crop image for multiple formats
        """
        
        pil_image:Image = Image.open(self._image_file)
        image_format = pil_image.format.lower()
        # Fixing EXIF
        pil_image = self._fix_exif(pil_image, image_format)

        cropping_results = list()
        for cropper in crop_data: 
            crop_format = (
                pil_image.width * cropper['x'] / cropper['image_width'],
                pil_image.height * cropper['y'] / cropper['image_height'],
                pil_image.width * (cropper['x'] + cropper['width']) / cropper['image_width'],
                pil_image.height * (cropper['y'] + cropper['height']) / cropper['image_height'],
            )
            cropped = pil_image.crop(crop_format)
            
            cropped_path = os.path.join(settings.PUBLIC_DIR, 'cropped')
            Path(cropped_path).mkdir(parents=True, exist_ok=True)
            
            output_filename = '.'.join((str(uuid.uuid4()), image_format))
            save_result = self._save_pil_image(cropped, output_filename, 'cropped')
            cropping_results.append(save_result)
        
        return cropping_results