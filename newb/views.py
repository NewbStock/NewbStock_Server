from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import StockKRTop100, StockUSTop100, HighKR, HighUS, Kospi, ExchangeRate, newssentiment, InterestRates
from .serializers import StockKRTop100Serializer, StockUSTop100Serializer, HighKRSerializer, HighUSASerializer
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import io, base64
import matplotlib
import os
from collections import defaultdict

matplotlib.use('Agg')

def get_country_data(country, kr_model, us_model, kr_serializer, us_serializer):
    if country == 'kr':
        queryset = kr_model.objects.all()[:3]
        serializer = kr_serializer(queryset, many=True)
    elif country == 'us':
        queryset = us_model.objects.all()[:3]
        serializer = us_serializer(queryset, many=True)
    else:
        return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_200_OK)

class StockTop3View(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code ('kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        country = request.query_params.get('country', 'kr').lower()
        return get_country_data(country, StockKRTop100, StockUSTop100, StockKRTop100Serializer, StockUSTop100Serializer)

class HighChangeStock(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code ('kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        country = request.query_params.get('country', 'kr').lower()
        
        if country == 'kr':
            queryset = HighKR.objects.all().order_by('-change')
            serializer_class = HighKRSerializer
        elif country == 'us':
            queryset = HighUS.objects.all().order_by('-change')
            serializer_class = HighUSASerializer
        else:
            return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)

        # 종목별로 상위 5개 항목을 선택
        grouped_data = defaultdict(list)
        for item in queryset:
            grouped_data[item.name].append(item)
            if len(grouped_data[item.name]) > 5:
                grouped_data[item.name] = grouped_data[item.name][:5]

        # 모든 그룹을 병합
        top_items = []
        for items in grouped_data.values():
            top_items.extend(items)

        # 시리얼라이즈
        serializer = serializer_class(top_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class KospiKosdaqChartView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="기준 날짜 (YYYY-MM-DD 형식)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "날짜가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=10)
            end_date = target_date + timedelta(days=10)
            dates, kospi_values, kosdaq_values = [], [], []

            for current_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                current_date_db_format = current_date.strftime('%Y%m%d')  # 데이터베이스에 저장된 형식에 맞게 변환
                kospi_entry = Kospi.objects.filter(time=current_date_db_format).first()

                print(f"Querying for date: {current_date_db_format}, result: {kospi_entry}")

                if kospi_entry:
                    dates.append(current_date.strftime('%Y-%m-%d'))
                    kospi_values.append(float(kospi_entry.kospi) if kospi_entry.kospi else kospi_values[-1] if kospi_values else 0.0)
                    kosdaq_values.append(float(kospi_entry.kosdaq) if kospi_entry.kosdaq else kosdaq_values[-1] if kosdaq_values else 0.0)

            if not dates or not kospi_values or not kosdaq_values:  # 데이터가 없는 경우
                return Response({"error": "해당 기간에 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # JSON 형식으로 데이터 반환
            return Response({
                "dates": dates,
                "kospi_values": kospi_values,
                "kosdaq_values": kosdaq_values
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangeRateChartView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="기준 날짜 (YYYY-MM-DD 형식)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "날짜가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=10)
            end_date = target_date + timedelta(days=10)
            dates, yen_values, dollar_values, yuan_values = [], [], [], []

            for current_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                current_date_db_format = current_date.strftime('%Y%m%d')
                exchange_entry = ExchangeRate.objects.filter(time=current_date_db_format).first()
                if exchange_entry:
                    dates.append(current_date.strftime('%Y-%m-%d'))
                    yen_values.append(float(exchange_entry.yen_100) if exchange_entry.yen_100 else yen_values[-1] if yen_values else 0.0)
                    dollar_values.append(float(exchange_entry.dollar) if exchange_entry.dollar else dollar_values[-1] if dollar_values else 0.0)
                    yuan_values.append(float(exchange_entry.yuan) if exchange_entry.yuan else yuan_values[-1] if yuan_values else 0.0)

            if not dates:  # 데이터가 없을 경우 기본 값을 넣음
                return Response({"error": "해당 기간에 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # JSON 형식으로 데이터 반환
            return Response({
                "dates": dates,
                "yen_values": yen_values,
                "dollar_values": dollar_values,
                "yuan_values": yuan_values
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class NewsSentimentChartView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="기준 날짜 (YYYY-MM-DD 형식)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "날짜가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=10)
            end_date = target_date + timedelta(days=10)
            dates, sentiment_values = [], []

            for current_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                current_date_db_format = current_date.strftime('%Y%m%d')
                sentiment_entry = newssentiment.objects.filter(time=current_date_db_format).first()
                if sentiment_entry:
                    dates.append(current_date.strftime('%Y-%m-%d'))
                    sentiment_values.append(float(sentiment_entry.sentiment) if sentiment_entry.sentiment else sentiment_values[-1] if sentiment_values else 0.0)

            if not dates:  # 데이터가 없을 경우
                return Response({"error": "해당 기간에 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # JSON 형식으로 데이터 반환
            return Response({
                "dates": dates,
                "sentiment_values": sentiment_values
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InterestRateChartView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="기준 날짜 (YYYY-MM-DD 형식)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "날짜가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=10)
            end_date = target_date + timedelta(days=10)
            dates, treasury_10y_values, treasury_2y_values, koribor_12m_values = [], [], [], []

            for current_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                current_date_db_format = current_date.strftime('%Y%m%d')
                interest_entry = InterestRates.objects.filter(time=current_date_db_format).first()
                if interest_entry:
                    dates.append(current_date.strftime('%Y-%m-%d'))
                    treasury_10y_values.append(float(interest_entry.treasury_10y) if interest_entry.treasury_10y else treasury_10y_values[-1] if treasury_10y_values else 0.0)
                    treasury_2y_values.append(float(interest_entry.treasury_2y) if interest_entry.treasury_2y else treasury_2y_values[-1] if treasury_2y_values else 0.0)
                    koribor_12m_values.append(float(interest_entry.koribor_12m) if interest_entry.koribor_12m else koribor_12m_values[-1] if koribor_12m_values else 0.0)

            if not dates:  # 데이터가 없을 경우
                return Response({"error": "해당 기간에 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # JSON 형식으로 데이터 반환
            return Response({
                "dates": dates,
                "treasury_10y_values": treasury_10y_values,
                "treasury_2y_values": treasury_2y_values,
                "koribor_12m_values": koribor_12m_values
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

