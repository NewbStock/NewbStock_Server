from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

class InvestmentDataView(APIView):
    """
    API to receive and store investment data.
    """

    def post(self, request):
        serializer = InvestmentCalculationSerializer(data=request.data)
        if serializer.is_valid():
            # 데이터를 받아서 처리 (예: 데이터베이스에 저장)
            # 여기서는 데이터를 세션에 임시 저장하는 예를 사용
            request.session['investment_data'] = serializer.validated_data
            return Response({"message": "Investment data received successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CalculateReturnsView(APIView):
    """
    API to calculate returns based on stored investment data.
    """

    def get(self, request):
        # 세션에서 저장된 데이터를 가져옴
        investment_data = request.session.get('investment_data')
        if not investment_data:
            raise ValidationError("No investment data found. Please submit data first.")

        company = investment_data['company']
        initial_amount = investment_data['initial_amount']
        initial_date = investment_data['initial_date']
        additional_amount = investment_data.get('additional_amount', 0)
        frequency = investment_data.get('frequency', None)

        # 예시 로직: 주식 데이터를 조회하여 수익률을 계산합니다.
        try:
            if "KR" in company:  # 한국 주식
                stock_data = KRSTOCKDATA.objects.filter(name=company, date__gte=initial_date).order_by('date')
            else:  # 미국 주식
                stock_data = USSTOCKDATA.objects.filter(name=company, date__gte=initial_date).order_by('date')

            # 단순히 첫 번째와 마지막 데이터의 open_value를 비교하여 수익률을 계산하는 예시
            if stock_data.exists():
                start_value = stock_data.first().open_value
                end_value = stock_data.last().open_value
                profit = (end_value - start_value) / start_value * 100  # 수익률 계산

                result = {
                    "company": company,
                    "initial_amount": initial_amount,
                    "initial_date": initial_date,
                    "additional_amount": additional_amount,
                    "frequency": frequency,
                    "profit_percentage": round(profit, 2)
                }
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No stock data found for the given period."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
