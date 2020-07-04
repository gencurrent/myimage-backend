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
        original_data = cache.get(cache_key, None)
        if original_data is None:
            logger.warning(f'{self.__class__.__name__}: the cache operation is not found')
            return Response(status=status.HTTP_404_NOT_FOUND)

        data_to_save = validated_data
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
        original_data = cache.get(cache_key, None)
        if original_data is None:
            logger.warning(f'{self.__class__.__name__}: the cache operation is not found')
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

        saving_results = {}
        for f, _file in files_read.items():
            try: 
                img_ops = ImageOperations(client_uuid, file_read)
                op_result = img_ops.resize_image_single(original_data)
                saving_results[f] = op_result
            except Exception as e:
                logger.warning(f'{self.__class__.__name__}: error while reading image: {e}')
                return Response(status=status.HTTP_400_BAD_REQUEST)
        logger.info(saving_results)

        return Response(dict( (k, {'uri': sr['public']}) for k, sr in saving_results.items() ), status=status.HTTP_200_OK)


# class ResizeSingleImageApiView(APIView):
    
#     def post(self, request, resize_uuid):
#         """
#         Reszie and save a single image to return it to the client
#         """

#         # Handling client UUID
#         client_uuid = request.COOKIES.get('X-Client-UUID')
#         if client_uuid is None:
#             response = Response('X-Client-UUID is required', 400)
#             return response

#         # Getting crop data
#         cache_data = cache.get(client_uuid, {})
#         if not cache_data:
#             logger.error(f'{self.__class__.__name__} -> Resize cache for client {client_uuid} not found')
#             return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         resize_data = cache_data.get('resizeData')
#         if not resize_data:
#             logger.error(f'{self.__class__.__name__} -> put -> Resize data for client {client_uuid} not found')
#             return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         logger.debug(resize_data)
#         operation_instance = resize_data.get(resize_uuid)
        
#         if not operation_instance:
#             return Response(data='Resize Instance not found', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         files = request.FILES
#         image_file = files.get('image')
#         if not image_file:
#             logger.error(f'{self.__class__.__name__} -> File not supplied for client UUID: {client_uuid}')
#             return Response(None, status=status.HTTP_403_FORBIDDEN)

#         file_read = None
#         try: 
#             image_data = image_file.read()
#             file_read = io.BytesIO(image_data)
#         except Exception as e:
#             logger.error(f'{self.__class__.__name__}: error while reading image data: {e}')
#             return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#         img_ops = ImageOperations(client_uuid, file_read)
#         ops_result = img_ops.resize_image_single(operation_instance)

#         return Response(ops_result.get('public'), status=status.HTTP_200_OK)

