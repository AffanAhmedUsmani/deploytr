from django.conf import settings
from django.http import JsonResponse


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith("/admin"):
            return self.get_response(request)

        api_key = request.headers.get("X-API-KEY")
        if api_key != settings.API_KEY:
            return JsonResponse({"error": "Invalid API key"}, status=401)

        response = self.get_response(request)
        return response
