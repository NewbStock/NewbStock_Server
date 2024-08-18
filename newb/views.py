from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import StockKRTop100, StockUSTop100, HighKR, HighUS, Kospi, ExchangeRate, newssentiment, InterestRates, StockKRHistory, StockUSHistory
from .serializers import StockKRTop100Serializer, StockUSTop100Serializer, HighKRSerializer, HighUSASerializer, StockKRHistory, StockUSHistory, StockKRHistorySerializer, StockUSHistorySerializer
from datetime import timedelta, datetime
from collections import defaultdict

# 국가별 데이터 조회 함수
def get_country_data(country, kr_model, us_model, kr_serializer, us_serializer):
    if country == 'kr':
        queryset = kr_model.objects.all()[:3]
        serializer = kr_serializer(queryset, many=True)
    elif country == 'us':
        queryset = us_model.objects.all()[:3]
        serializer = us_serializer(queryset, many=True)
    else:
        return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)
    return serializer.data

# 1년치 open_value 데이터를 조회하는 함수
def get_yearly_open_values(stock_name, history_model, history_serializer):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=365)
    
    queryset = history_model.objects.filter(name=stock_name, date__range=[start_date, end_date]).order_by('date')
    serializer = history_serializer(queryset, many=True)
    return serializer.data

# 날짜 범위에 따른 데이터 조회 함수
def get_date_range_data(date_str, model, fields):
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_date = target_date - timedelta(days=10)
        end_date = target_date + timedelta(days=10)
        dates = []
        data_dict = {field: [] for field in fields}

        for current_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
            current_date_db_format = current_date.strftime('%Y%m%d')
            entry = model.objects.filter(time=current_date_db_format).first()
            if entry:
                dates.append(current_date.strftime('%Y-%m-%d'))
                for field in fields:
                    value = getattr(entry, field, None)
                    data_dict[field].append(float(value) if value else (data_dict[field][-1] if data_dict[field] else 0.0))

        if not dates:
            return Response({"error": "해당 기간에 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"dates": dates, **data_dict}, status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 상위 3개 종목 조회 API
# 상위 3개 종목 및 1년치 open_value 조회 API
class StockTop3View(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code ('kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        country = request.query_params.get('country', 'kr').lower()
        
        # 상위 3개 종목 데이터 가져오기
        top3_data = get_country_data(country, StockKRTop100, StockUSTop100, StockKRTop100Serializer, StockUSTop100Serializer)

        # 1년치 open_value 데이터를 위한 모델 및 시리얼라이저 설정
        if country == 'kr':
            history_model = StockKRHistory
            history_serializer = StockKRHistorySerializer
        elif country == 'us':
            history_model = StockUSHistory
            history_serializer = StockUSHistorySerializer
        else:
            return Response({"error": "Invalid country code."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 각 종목에 대한 1년치 open_value 데이터 가져오기
        for stock in top3_data:
            stock_name = stock['name']
            stock['yearly_open_values'] = get_yearly_open_values(stock_name, history_model, history_serializer)

        return Response(top3_data, status=status.HTTP_200_OK)
# 높은 변동성 종목 조회 API
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
        top_items = [item for items in grouped_data.values() for item in items]

        # 시리얼라이즈
        serializer = serializer_class(top_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# KOSPI/KOSDAQ 차트 데이터 조회 API
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
        return get_date_range_data(date_str, Kospi, ['kospi', 'kosdaq'])

# 환율 차트 데이터 조회 API
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
        return get_date_range_data(date_str, ExchangeRate, ['yen_100', 'dollar', 'yuan'])

# 뉴스 감성 차트 데이터 조회 API
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
        return get_date_range_data(date_str, newssentiment, ['sentiment'])

# 금리 차트 데이터 조회 API
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
        return get_date_range_data(date_str, InterestRates, ['treasury_10y', 'treasury_2y', 'koribor_12m'])
