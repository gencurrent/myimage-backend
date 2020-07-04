"""
    A middleware for the system requests
"""

class SystemMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if hasattr(request, 'client-uui')
        response = self.get_response()
        return response