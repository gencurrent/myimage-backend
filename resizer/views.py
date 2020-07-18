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

from .serializers import ResizeImageSerializer
from utils import ImageOperations

logger = logging.getLogger(__name__)

class ResizerSetDataSingle(APIView):
    def post(self, request, op_uuid):
        """
            Save data about future resizing
        """

        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        data = request.data
        plain_data = data

        ss = ResizeImageSerializer(data=plain_data)
        if not ss.is_valid():
            return Response(ss.errors, status.HTTP_400_BAD_REQUEST)

        validated_data = ss.data
        cache_key = f'{client_uuid}_resize_{op_uuid}'
        
        # Get original cached data
        original_data = cache.get(cache_key, None)
        if original_data is None:
            logger.warning(f'{self.__class__.__name__}: the cache operation is not found')
            return Response(status=status.HTTP_404_NOT_FOUND)

        data_to_save = {
            'input': validated_data # Input data for the future operations
        }
        cache.set(cache_key, data_to_save, 1 * 60 * 60)
        response = Response(ss.data, status=200)
        return response


class ResizeManyImagesApiView(APIView):
    def post(self, request, op_uuid):
        """
        Reszie and save multiple images to return it to the client by Operation UUID key
        """
        # Handling client UUID
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        cache_key = f'{client_uuid}_resize_{op_uuid}'
        operation_data = cache.get(cache_key, None)
        # Get the whole operation data
        if operation_data is None:
            logger.warning(f'{self.__class__.__name__}: the cache operation is not found')
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Get the input data
        input_data = operation_data.get('input')
        if input_data is None:
            logger.warning(f'{self.__class__.__name__}: the cache operation input data is not found')
            return Response(status=status.HTTP_404_NOT_FOUND)

        files = request.FILES
        if not files:
            logger.warning('{self.__class__.__name__}: no files were uploaded')
            return Response('No files uploaded', status=status.HTTP_400_BAD_REQUEST)

        files_read = {}
        for f, _file in files.items():
            try: 
                image_data = _file.read()
                file_read = io.BytesIO(image_data)
                files_read[f] = file_read
            except Exception as e:
                logger.error(f'{self.__class__.__name__}: error while reading file: {e}')
                return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # The operation itself
        ops_result = {}
        for f, _file in files_read.items():
            try: 
                img_ops = ImageOperations(client_uuid, file_read)
                op_result = img_ops.resize_image_single(input_data)
                ops_result[f] = op_result
            except Exception as e:
                logger.warning(f'{self.__class__.__name__}: error while reading image: {e}')
                return Response(status=status.HTTP_400_BAD_REQUEST)
        logger.info(ops_result)

        # Save the result into the cache
        operation_data.update({'results': ops_result})
        cache.set(cache_key, operation_data, 1 * 60 * 60)
        logger.info(operation_data)

        to_return = dict( (k, {'uri': sr['public']}) for k, sr in ops_result.items() )
        return Response(to_return, status=status.HTTP_200_OK)

