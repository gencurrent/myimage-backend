import pdb
import io
import os
import uuid
import base64

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image

from .serializers import CropImageSerializer, NewCropperSerialier

# Create your views here.

class CropDataApiView(APIView):

    def post(self, request):
        """
        Add a new cropper data
        """
        
        data = {
            'uuid': str(uuid.uuid4())
        }
        return Response(data, status=200)

    def put(self, request):
        """
        Save a data about an image cropping parameters
        """
        data = request.data
        
        ss = CropImageSerializer(data=data, many=True)
        
        
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        if not ss.is_valid():
            return Response(ss.errors, 400)
        
        # pdb.set_trace()
        validated_data = ss.data
        for crop_data in validated_data:
            if crop_data.get('uuid') is None:
                crop_data['uuid'] = str(uuid.uuid4())
        save_to = dict({'cropData': list(validated_data)})
        cache.set(client_uuid, save_to)
        response = Response(ss.data, status=200)
        return response


class CropImageApiView(APIView):

    def post(self, request):
        """
        Save a an image and crop it
        """
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        files = request.FILES
        
        image_file = files.get('image')
        image_extension = image_file.name.split('.')[-1]
        image_data = image_file.read()
        pil_image = Image.open(io.BytesIO(image_data))

        crop_data = cache.get(client_uuid)
        if crop_data is None:
            return Response(data={'error': 'The cropper data is not found'}, status=status.HTTP_404_NOT_FOUND)
        crop_data = crop_data.get('cropData')
        uuid_url = dict()
        for cropper in crop_data: 
            crop_data = (
                pil_image.width * cropper['x'] / cropper['image_width'],
                pil_image.height * cropper['y'] / cropper['image_height'],
                pil_image.width * (cropper['x'] + cropper['width']) / cropper['image_width'],
                pil_image.height * (cropper['y'] + cropper['height']) / cropper['image_height'],
            )
            cropped = pil_image.crop(crop_data)
            output_filename = '.'.join((str(uuid.uuid4()), image_extension))
            output_path = os.path.join(settings.PUBLIC_DIRECTORY, 'cropped', output_filename)
            cropped.save(output_path)
            
            crop_uuid = str(cropper.get('uuid'))
            uuid_url[crop_uuid] = output_path
        
        return Response(uuid_url, status=status.HTTP_200_OK)