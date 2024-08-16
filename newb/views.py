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

class StockPriceChangeView(APIView):
    """
    API to receive a stock name and return the price change percentages over time.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('company', openapi.IN_QUERY, description="Stock name", type=openapi.TYPE_STRING),
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code (e.g., 'kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        company = request.query_params.get('company')
        country = request.query_params.get('country', 'kr')

        if not company:
            return Response({"error": "company parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 주식 데이터 조회
            if country.lower() == "kr":  # 한국 주식
                stock_data = KRSTOCKDATA.objects.filter(name=company).order_by('date')
            else:  # 미국 주식 (또는 다른 나라 주식 추가 가능)
                stock_data = USSTOCKDATA.objects.filter(name=company).order_by('date')

            if not stock_data.exists():
                return Response({"error": "No stock data found for the given company."}, status=status.HTTP_404_NOT_FOUND)

            # 변동률 계산
            price_changes = []
            previous_value = None
            for stock in stock_data:
                if previous_value is not None:
                    change = (stock.open_value - previous_value) / previous_value * 100
                    price_changes.append({
                        "date": stock.date,
                        "price_change_percentage": round(change, 2)
                    })
                previous_value = stock.open_value

            return Response({"company": company, "price_changes": price_changes}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)