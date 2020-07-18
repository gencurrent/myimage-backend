import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ResultView(APIView):
    """
    Single result operations
    """

    def get(self, request, operation, operation_uuid):
        """
        Get the operation result
        :param operation str: operation available 
            in the system {'crop', 'resize', 'crop-multiformat'} (see the system.views )
        :param operaion_uui str: the UUID of the operation
        """
        client_uuid = request.COOKIES.get('X-Client-UUID')
        if client_uuid is None:
            response = Response('X-Client-UUID is required', 400)
            return response

        cache_key = f'{client_uuid}_{operation}_{operation_uuid}'
        operation_cache = cache.get(cache_key)
        if operation_cache is None:
            logger.warning(f'{self.__class__.__name__}: the operation {operation_uuid} results are not found in cache')
            resp = Response(status=status.HTTP_404_NOT_FOUND)
            return resp

        ops_results = operation_cache.get('results')
        if ops_results is None:
            logger.warning(f'{self.__class__.__name__}: the operation\'s {operation_uuid} results are not found in cache')
            resp = Response(status=status.HTTP_404_NOT_FOUND)
            return resp
        logger.info(ops_results)

        # Iteration over keys of the operation
        for k, v in ops_results.items():
            del v['saved']
        logger.info(ops_results)
        # ops_results_public = ops_results.get('public')
        # if ops_results_public is None:
        #     logger.warning(f'{self.__class__.__name__}: the operation\'s {operation_uuid} public results are not found  in cache')
        #     resp = Response(status=status.HTTP_404_NOT_FOUND)
        #     return resp
        
        resp = Response(ops_results, status=status.HTTP_200_OK)
        return resp