from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import StockKRTop100, StockUSTop100
from .serializers import StockKRTop100Serializer, StockUSTop100Serializer

class StockTop3View(APIView):
    """
    API to return the top 3 entries in the StockKRTop100 or StockUSTop100 table based on the country code.
    """
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code ('kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        country = request.query_params.get('country', 'kr').lower()
        
        if country == 'kr':
            queryset = StockKRTop100.objects.all()[:3]  # 한국 주식 상위 3개 항목
            serializer = StockKRTop100Serializer(queryset, many=True)
        elif country == 'us':
            queryset = StockUSTop100.objects.all()[:3]  # 미국 주식 상위 3개 항목
            serializer = StockUSTop100Serializer(queryset, many=True)
        else:
            return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

