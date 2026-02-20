from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ai_root_view(request):
    """AI Engine root endpoint"""
    return Response({
        "name": "Foodis AI Engine",
        "description": "Smart recommendation and analytics engine",
        "status": "integrated",
        "endpoints": {
            "trending": "/api/client/trending/",
            "recommendations": "/api/client/recommendations/"
        }
    }, status=status.HTTP_200_OK)
