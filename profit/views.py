from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import InvestmentCalculationSerializer
from datetime import date
from django.db import connection
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)

class InvestmentDataView(APIView):
    """
    API to receive investment data, calculate returns, and return the result.
    """

    @swagger_auto_schema(request_body=InvestmentCalculationSerializer)
    def post(self, request):
        serializer = InvestmentCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            if isinstance(data['initial_date'], date):
                initial_date = data['initial_date']
            else:
                initial_date = date.fromisoformat(data['initial_date'])

            country = data['country'].lower()  # 추가된 country 필드 (kr 또는 us)
            company = data['company']
            initial_inv = data['initial_amount']
            additional_inv = data.get('additional_amount', 0)
            frequency_map = {'weekly': 5, 'biweekly': 10, 'monthly': 20, 'bimonthly': 40}
            frequency = frequency_map.get(data.get('frequency'))

            # 테이블 선택 (kr_stock_data 또는 us_stock_data)
            if country == 'kr':
                table_name = 'kr_stock_data'
            elif country == 'us':
                table_name = 'us_stock_data'
            else:
                return Response({"error": "Invalid country specified."}, status=status.HTTP_400_BAD_REQUEST)

            sql_query = f"""
                WITH InvestmentDates AS (
                  SELECT date, rn
                  FROM (
                    SELECT date, ROW_NUMBER() OVER (ORDER BY date) AS rn
                    FROM {table_name}
                    WHERE name = %s AND date >= %s
                  ) subquery
                  WHERE rn = 1 OR (rn - 1) %% %s = 0
                ),
                PurchaseData AS (
                  SELECT 
                    i.date,
                    k.open_value,
                    CASE WHEN k.open_value = 0 THEN 0
                         WHEN i.rn = 1 THEN %s ELSE %s END AS investment,
                    CASE WHEN k.open_value = 0 THEN 0
                         WHEN i.rn = 1 THEN %s / k.open_value 
                         ELSE %s / k.open_value END AS purchased_shares
                  FROM InvestmentDates i
                  JOIN {table_name} k ON i.date = k.date AND k.name = %s
                ),
                TotalCalculations AS (
                  SELECT 
                    SUM(purchased_shares) AS total_shares,
                    SUM(investment) AS total_investment
                  FROM PurchaseData
                )
                SELECT 
                  total_shares,
                  total_investment,
                  TRUNC((SELECT open_value FROM {table_name} WHERE name = %s AND open_value > 0 ORDER BY date DESC LIMIT 1) * total_shares - total_investment) AS total_profit_loss
                FROM TotalCalculations;
            """

            try:
                # 디버깅용 로그 추가
                logger.debug(f"Executing SQL query with params: company={company}, initial_date={initial_date}, frequency={frequency}, initial_inv={initial_inv}, additional_inv={additional_inv}, table={table_name}")

                # SQL 쿼리를 실행하고 결과를 가져옴
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, (
                        company, 
                        initial_date, 
                        frequency, 
                        initial_inv, 
                        additional_inv, 
                        initial_inv, 
                        additional_inv, 
                        company, 
                        company
                    ))
                    result = cursor.fetchone()
                
                if result:
                    total_shares, total_investment, total_profit_loss = result
                    response_data = {
                        "company": company,
                        "initial_amount": initial_inv,
                        "initial_date": initial_date.strftime('%Y-%m-%d'),
                        "additional_amount": additional_inv,
                        "frequency": data.get('frequency'),
                        "total_shares": total_shares,
                        "total_investment": total_investment,
                        "total_profit_loss": total_profit_loss
                    }
                    logger.debug(f"Query Result: {response_data}")
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.debug("No data found for the given parameters.")
                    return Response({"error": "Calculation failed, no data found."}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                logger.error(f"Unexpected error occurred: {str(e)}")
                return Response({"error": f"Unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
