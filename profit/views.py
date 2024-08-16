from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .serializers import InvestmentCalculationSerializer
from .models import KRSTOCKDATA, USSTOCKDATA
from datetime import date, timedelta
import calendar
from drf_yasg.utils import swagger_auto_schema

class InvestmentDataView(APIView):
    """
    API to receive investment data, calculate returns, and return the result.
    """
    def get_next_investment_date(self, current_date, frequency):
        """
        주기(frequency)에 따라 다음 투자 날짜를 계산합니다.
        """
        if frequency == "monthly":
            # 다음 달의 첫 번째 날짜
            month = current_date.month + 1 if current_date.month < 12 else 1
            year = current_date.year if month > 1 else current_date.year + 1
            return date(year, month, 1)
        elif frequency == "biweekly":
            return current_date + timedelta(weeks=2)
        elif frequency == "weekly":
            return current_date + timedelta(weeks=1)
        else:
            # 기본적으로 월간으로 처리
            month = current_date.month + 1 if current_date.month < 12 else 1
            year = current_date.year if month > 1 else current_date.year + 1
            return date(year, month, 1)
        
    @swagger_auto_schema(request_body=InvestmentCalculationSerializer)
    def post(self, request):
        # JSON 데이터를 받아옴
        serializer = InvestmentCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # date 객체를 문자열로 변환
            if isinstance(data['initial_date'], date):
                data['initial_date'] = data['initial_date'].strftime('%Y-%m-%d')
            
            # 투자 데이터 기반으로 수익률 계산
            try:
                country = data['country']
                company = data['company']
                initial_amount = data['initial_amount']
                initial_date = date.fromisoformat(data['initial_date'])
                additional_amount = data.get('additional_amount', 0)
                frequency = data.get('frequency')

                # 주식 데이터를 조회
                if country.lower() == "kr":  # 한국 주식
                    stock_data = KRSTOCKDATA.objects.filter(name=company, date__gte=initial_date).order_by('date')
                else:  # 미국 주식 (또는 다른 나라 주식 추가 가능)
                    stock_data = USSTOCKDATA.objects.filter(name=company, date__gte=initial_date).order_by('date')

                if not stock_data.exists():
                    return Response({"error": "No stock data found for the given period."}, status=status.HTTP_404_NOT_FOUND)

                # 초기 값 설정
                total_investment = initial_amount
                total_shares = initial_amount / stock_data.first().open_value
                current_date = initial_date

                # 정기 투자에 따른 수익률 계산
                for stock in stock_data:
                    if stock.date >= current_date:
                        # 다음 투자일인지 확인
                        if stock.date == current_date:
                            total_investment += additional_amount
                            total_shares += additional_amount / stock.open_value
                            current_date = self.get_next_investment_date(current_date, frequency)

                # 마지막 날의 투자 가치 계산
                final_value = total_shares * stock_data.last().open_value
                profit = (final_value - total_investment) / total_investment * 100  # 수익률 계산

                result = {
                    "company": company,
                    "initial_amount": initial_amount,
                    "initial_date": data['initial_date'],
                    "additional_amount": additional_amount,
                    "frequency": frequency,
                    "final_value": round(final_value, 2),
                    "profit_percentage": round(profit, 2)
                }
                return Response(result, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"Unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)