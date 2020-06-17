import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

class SystemApi(APIView):
    def get(self, request):
        response = Response(None, HTTP_200_OK)
        client_uuid = request.COOKIES.get('X-Client-UUID')
        
        if not client_uuid:
            client_uuid = str(uuid.uuid4())
            response = Response(HTTP_200_OK)
            response.set_cookie('X-Client-UUID', client_uuid)
        print(f'Set the system X-Client-UUID header: {client_uuid}')
        response.set_cookie('X-Client-UUID', client_uuid)
        return response