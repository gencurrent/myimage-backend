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


class CropperSetDataSingle(APIView):
    def post(self, request, op_uuid):
        """
        Save data about future cropping
        """
        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        plain_data = request.data

        ss = CropImageSerializer(data=plain_data)
        if not ss.is_valid():
            return Response(ss.errors, 400)
        
        validated_data = ss.data
        cache_key = f'{client_uuid}_crop_{op_uuid}'
        cache.set(cache_key, dict(validated_data), 60 * 30)
        response = Response(ss.data, status=200)
        return response


class CropperSetData(APIView):
    def post(self, request, op_uuid):
        """
        Save data about future cropping
        :param op_uuid str: the UUID of the whole multoformat-crop operation
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        data = request.data
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
        
        cache_keys_saved = []
        for crop_data in plain_data:
            sub_op_uuid = crop_data.get('uuid')
            if sub_op_uuid is None:
                logger.error(f'{self.__class__.__name__}: operation UUID is None')
                return Response(500)
            cache_key = f'{client_uuid}_crop_{sub_op_uuid}'
            cache.set(cache_key, crop_data, 60 * 60)
            cache_keys_saved.append(cache_key)
        
        # Save the array of keys to the main crop data cache
        cache_key_main = f'{client_uuid}_crop-multiformat_{op_uuid}'
        cache.set(cache_key_main, cache_keys_saved, 60 * 60)

        return Response(ss.data, status=200)

        


class CropSingleImageApiView(APIView):
    
    def post(self, request, op_uuid):
        """
        Crop and save a single image to the disk
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        # Getting crop data
        cache_key = f'{client_uuid}_crop_{op_uuid}'
        cached_data = cache.get(cache_key, {})
        if not cached_data:
            logger.error(f'CropSingleImageApiView -> Crop cache for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(cached_data)

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
        ops_result = img_ops.crop_image_single(cached_data)

        return Response(ops_result, status=status.HTTP_200_OK)



class CropImageApiView(APIView):
    """
        Class for cropping multiple formats
    """
    def post(self, request, op_uuid):
        """
        Save all the images and crop them
        :param op_uuid str: the main operation UUID
        """
        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        
        # Getting crop data
        cache_key = f'{client_uuid}_crop-multiformat_{op_uuid}'
        main_crop_cache = cache.get(cache_key, [])
        if not main_crop_cache:
            logger.error(f'{self.__class__.__name__}: Main crop cache for client {client_uuid} not found')
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        crop_caches = []
        for crop_key in main_crop_cache:
            crop_cache = cache.get(crop_key, None)
            if not crop_cache:
                logger.error(f'{self.__class__.__name__}: SubCrop cache for client {client_uuid} not found')
                return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            crop_caches.append(crop_cache)
        
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
        cropping_results = img_ops.crop_image_multiformat(crop_caches)

        
        return Response(cropping_results, status=status.HTTP_200_OK)