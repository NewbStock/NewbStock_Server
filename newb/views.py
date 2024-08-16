from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import *
from .serializers import *
import matplotlib.pyplot as plt
from datetime import timedelta
import io
import base64
from datetime import datetime

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


class HighChangeStock(APIView):
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
            queryset = HighKR.objects.all()  # 한국 주식 상위 3개 항목
            serializer = HighKRSerializer(queryset, many=True)
        elif country == 'us':
            queryset = HighUS.objects.all()  # 미국 주식 상위 3개 항목
            serializer = HighUSASerializer(queryset, many=True)
        else:
            return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ChartViews(APIView):
    """
    KOSPI, KOSDAQ, 환율(엔화, 달러, 위안), 뉴스 심리지수, 금리(10년 국채, 2년 국채, Koribor 12M)의 차트를 생성하는 API
    """
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="기준 날짜 (YYYY-MM-DD 형식)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        date_str = request.query_params.get('date', None)
        
        if not date_str:
            return Response({"error": "날짜가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 입력된 날짜를 기준으로 10일 전후의 기간 설정
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=10)
            end_date = target_date + timedelta(days=10)
            
            # 초기화할 리스트들
            dates = []
            kospi_values = []
            kosdaq_values = []
            yen_values = []
            dollar_values = []
            yuan_values = []
            sentiment_values = []
            treasury_10y_values = []
            treasury_2y_values = []
            koribor_12m_values = []
            
            # 시작 날짜부터 종료 날짜까지 순회
            current_date = start_date
            while current_date <= end_date:
                # 현재 날짜의 데이터를 가져옴
                kospi_entry = Kospi.objects.filter(time=current_date).first()
                exchange_entry = ExchangeRate.objects.filter(time=current_date).first()
                sentiment_entry = newssentiment.objects.filter(time=current_date).first()
                interest_entry = InterestRates.objects.filter(time=current_date).first()

                # 날짜 추가
                dates.append(current_date.strftime('%Y-%m-%d'))

                # KOSPI 및 KOSDAQ 값을 추가 (데이터가 없으면 이전 값 사용)
                if kospi_entry:
                    kospi_values.append(float(kospi_entry.kospi) if kospi_entry.kospi is not None else kospi_values[-1])
                    kosdaq_values.append(float(kospi_entry.kosdaq) if kospi_entry.kosdaq is not None else kosdaq_values[-1])
                else:
                    kospi_values.append(kospi_values[-1] if kospi_values else 0.0)
                    kosdaq_values.append(kosdaq_values[-1] if kosdaq_values else 0.0)

                # 환율 데이터를 추가 (데이터가 없으면 이전 값 사용)
                if exchange_entry:
                    yen_values.append(float(exchange_entry.yen_100) if exchange_entry.yen_100 is not None else yen_values[-1])
                    dollar_values.append(float(exchange_entry.dollar) if exchange_entry.dollar is not None else dollar_values[-1])
                    yuan_values.append(float(exchange_entry.yuan) if exchange_entry.yuan is not None else yuan_values[-1])
                else:
                    yen_values.append(yen_values[-1] if yen_values else 0.0)
                    dollar_values.append(dollar_values[-1] if dollar_values else 0.0)
                    yuan_values.append(yuan_values[-1] if yuan_values else 0.0)

                # 뉴스 심리지수 값을 추가 (데이터가 없으면 이전 값 사용)
                if sentiment_entry:
                    sentiment_values.append(float(sentiment_entry.sentiment) if sentiment_entry.sentiment is not None else sentiment_values[-1])
                else:
                    sentiment_values.append(sentiment_values[-1] if sentiment_values else 0.0)

                # 금리 데이터를 추가 (데이터가 없으면 이전 값 사용)
                if interest_entry:
                    treasury_10y_values.append(float(interest_entry.treasury_10y) if interest_entry.treasury_10y is not None else treasury_10y_values[-1])
                    treasury_2y_values.append(float(interest_entry.treasury_2y) if interest_entry.treasury_2y is not None else treasury_2y_values[-1])
                    koribor_12m_values.append(float(interest_entry.koribor_12m) if interest_entry.koribor_12m is not None else koribor_12m_values[-1])
                else:
                    treasury_10y_values.append(treasury_10y_values[-1] if treasury_10y_values else 0.0)
                    treasury_2y_values.append(treasury_2y_values[-1] if treasury_2y_values else 0.0)
                    koribor_12m_values.append(koribor_12m_values[-1] if koribor_12m_values else 0.0)

                # 다음 날짜로 이동
                current_date += timedelta(days=1)

            # KOSPI와 KOSDAQ 차트 생성
            plt.figure(figsize=(10, 5))
            plt.plot(dates, kospi_values, label='KOSPI', marker='o', color='blue')
            plt.plot(dates, kosdaq_values, label='KOSDAQ', marker='o', color='green')
            plt.xticks(rotation=45)
            plt.xlabel('Date')
            plt.ylabel('Index Value')
            plt.title('KOSPI and KOSDAQ Indices')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            kospi_kosdaq_img = io.BytesIO()
            plt.savefig(kospi_kosdaq_img, format='png')
            kospi_kosdaq_img.seek(0)
            plt.close()

            # 환율 차트 (엔화, 달러, 위안) 생성
            plt.figure(figsize=(10, 5))
            plt.plot(dates, yen_values, label='100 Yen', marker='o', color='red')
            plt.plot(dates, dollar_values, label='Dollar', marker='o', color='blue')
            plt.plot(dates, yuan_values, label='Yuan', marker='o', color='purple')
            plt.xticks(rotation=45)
            plt.xlabel('Date')
            plt.ylabel('Exchange Rate')
            plt.title('Exchange Rates (100 Yen, Dollar, Yuan)')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            exchange_rate_img = io.BytesIO()
            plt.savefig(exchange_rate_img, format='png')
            exchange_rate_img.seek(0)
            plt.close()

            # 금리 차트 (10년 국채, 2년 국채, Koribor 12M) 생성
            plt.figure(figsize=(10, 5))
            plt.plot(dates, treasury_10y_values, label='10Y Treasury', marker='o', color='brown')
            plt.plot(dates, treasury_2y_values, label='2Y Treasury', marker='o', color='orange')
            plt.plot(dates, koribor_12m_values, label='Koribor 12M', marker='o', color='purple')
            plt.xticks(rotation=45)
            plt.xlabel('Date')
            plt.ylabel('Interest Rate (%)')
            plt.title('Interest Rates (10Y Treasury, 2Y Treasury, Koribor 12M)')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            interest_rate_img = io.BytesIO()
            plt.savefig(interest_rate_img, format='png')
            interest_rate_img.seek(0)
            plt.close()

            # 뉴스 심리지수 차트 생성
            plt.figure(figsize=(10, 5))
            plt.plot(dates, sentiment_values, label='News Sentiment', marker='o', color='orange')
            plt.xticks(rotation=45)
            plt.xlabel('Date')
            plt.ylabel('Sentiment Score')
            plt.title('News Sentiment Index')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            sentiment_img = io.BytesIO()
            plt.savefig(sentiment_img, format='png')
            sentiment_img.seek(0)
            plt.close()

            # 차트를 base64로 인코딩
            kospi_kosdaq_img_base64 = base64.b64encode(kospi_kosdaq_img.getvalue()).decode('utf-8')
            exchange_rate_img_base64 = base64.b64encode(exchange_rate_img.getvalue()).decode('utf-8')
            interest_rate_img_base64 = base64.b64encode(interest_rate_img.getvalue()).decode('utf-8')
            sentiment_img_base64 = base64.b64encode(sentiment_img.getvalue()).decode('utf-8')

            return Response({
                "kospi_kosdaq_chart": kospi_kosdaq_img_base64,
                "exchange_rate_chart": exchange_rate_img_base64,
                "interest_rate_chart": interest_rate_img_base64,
                "sentiment_chart": sentiment_img_base64
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
