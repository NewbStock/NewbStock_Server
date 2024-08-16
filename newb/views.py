from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class StockTop3KR(APIView):
    """
    API to return the first top 3 entries in the StockKRTop100 table.
    """
    def get(self, request):
        queryset = StockKRTop100.objects.all()[:3]  # 가장 위의 3개 항목을 가져옴
        serializer = StockKRTop100Serializer(queryset, many=True)
        return Response(serializer.data)
    
class StockTop3US(APIView):
    """
    API to return the first top 3 entries in the StockUSTop100 table.
    """
    def get(self, request):
        queryset = StockUSTop100.objects.all()[:3]  # 가장 위의 3개 항목을 가져옴
        serializer = StockUSTop100Serializer(queryset, many=True)
        return Response(serializer.data)

