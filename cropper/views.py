import io
import os
import uuid
import base64
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image, ExifTags

from .serializers import CropImageSerializer
from utils import ImageOperations

logger = logging.getLogger(__name__)


class CropDataApiView(APIView):

    def post(self, request):
        """
        Add/Reset a client's data about cropping
        """
        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        crop_uuid = uuid.uuid4()
        cache.set(client_uuid, {'cropData': {}}, 60 * 60)
        return Response({'uuid': crop_uuid}, status=200)


class CropperSetDataSingle(APIView):
    def post(self, request, crop_uuid):
        """
        Save data about future cropping
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        data = request.data
        plain_data = data.get('crop')

        ss = CropImageSerializer(data=plain_data)
        if not ss.is_valid():
            return Response(ss.errors, 400)
        
        validated_data = ss.data

        original_data = cache.get(client_uuid, {})
        cache_data_key = 'cropData'
        cached_data = original_data.get(cache_data_key, {})
        cached_data[crop_uuid] = validated_data

        save_data = dict({cache_data_key: cached_data})
        cache.set(client_uuid, save_data, 60 * 30)
        response = Response(ss.data, status=200)
        return response


class CropperSetData(APIView):
    def post(self, request):
        """
        Save data about future cropping
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        data = request.data
        logger.info(f'{self.__class__.__name__} -> data = ')
        logger.info(data)
        plain_data = []
        
        for key, value in data.items():
            crop_format = value.get('crop')
            crop_format.update({
                'uuid': key
            })
            plain_data.append(crop_format)
        ss = CropImageSerializer(data=plain_data, many=True)
        if not ss.is_valid():
            return Response(ss.errors, 400)
        
        validated_data = ss.data
        logger.info('PlainData = ')
        logger.info(plain_data)
        for idx, crop_data in enumerate(validated_data):
            if crop_data.get('uuid') is None:
                validated_data[idx]['uuid'] = str(uuid.uuid4())
        save_data = dict({'cropData': list(validated_data)})
        logger.info(f'save_data ->')
        logger.info(save_data)
        cache.set(client_uuid, save_data, 60 * 30)
        response = Response(ss.data, status=200)
        return response

        


class CropSingleImageApiView(APIView):
    
    def post(self, request, crop_uuid):
        """
        Crop and save a single image to the disk
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        # Getting crop data
        crop_cache = cache.get(client_uuid, {})
        if not crop_cache:
            logger.error(f'CropSingleImageApiView -> Crop cache for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        crop_data = crop_cache.get('cropData')
        if not crop_data:
            logger.error(f'CropSingleImageApiView -> put -> Crop data for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(crop_data)
        crop_instance = None
        crop_instance = crop_data.get(crop_uuid)
        
        if not crop_instance:
            return Response(data='Crop instance not found', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        files = request.FILES
        image_file = files.get('image')
        if not image_file:
            logger.error(f'CropSingleImageApiView -> File not supplied for client UUID: {client_uuid}')
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        file_read = None
        try: 
            image_data = image_file.read()
            file_read = io.BytesIO(image_data)
        except Exception as e:
            logger.error(f'CropImageApiView: error while reading image data: {e}')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        img_ops = ImageOperations(client_uuid, file_read)
        ops_result = img_ops.crop_image_single(crop_instance)

        return Response(ops_result, status=status.HTTP_200_OK)



class CropImageApiView(APIView):
    """
        Class for cropping multiple formats
    """
    def post(self, request):
        """
        Save all the images and crop them
        """
        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        # Getting crop data
        crop_cache = cache.get(client_uuid, {})
        if not crop_cache:
            logger.error(f'Crop cache for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        crop_data = crop_cache.get('cropData')
        if not crop_data:
            logger.error(f'Crop data for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        files = request.FILES
        image_file = files.get('image')
        if not image_file:
            logger.error(f'File not supplied for client UUID: {client_uuid}')
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        try: 
            image_data = image_file.read()
            file_read = io.BytesIO(image_data)
        except Exception as e:
            logger.error(f'CropImageApiView: error while reading image data: {e}')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        img_ops = ImageOperations(client_uuid, file_read)
        cropping_results = img_ops.crop_image_multiformat(crop_data)

        
        return Response(cropping_results, status=status.HTTP_200_OK)