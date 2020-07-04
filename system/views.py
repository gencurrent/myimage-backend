import uuid
import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

logger = logging.getLogger(__name__)

class SystemApi(APIView):
    def get(self, request):
        response = Response(None, HTTP_200_OK)
        
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if not client_uuid:
            client_uuid = str(uuid.uuid4())
            response = Response(HTTP_200_OK)
            response.set_cookie('X-Client-UUID', client_uuid)
        response.set_cookie('X-Client-UUID', client_uuid)
        return response

class SystemOpUuid(APIView):
    """
        Init the system UUID for an operation
    """
    def get(self, request, operation):
        # X-Client-UUID requirement 
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response
        if not(operation in ('resize', 'crop', 'crop-multiple')):
            logger.warning(f'{self.__class__.__name__}: wrong operation supplied: {operation}')
            return Response({'error': 'Operation not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new Operation UUID and save it to the cache
        op_uuid = str(uuid.uuid4())
        cache_key = f'{client_uuid}_{operation}_{op_uuid}'
        cache.set(cache_key, {}, 60 * 60)

        return Response({'uuid': op_uuid}, status=200)