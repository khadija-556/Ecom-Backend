from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import universal_search

class UniversalSearchView(APIView):
    """
    API view to handle universal search requests.
    """

    def get(self, request):

        query = request.query_params.get('query')

        if not query:
            return Response({
                "search": None,
                "results": [],
            }, status=status.HTTP_200_OK)
        
        results = universal_search(query.strip())



        return Response({
                "search": query,
                "results": results,
            }, status=status.HTTP_200_OK)