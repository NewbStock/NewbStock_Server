from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import boto3
import pandas as pd
import io
import os
from datetime import datetime, timedelta

# Create your views here.
class s3newsgetView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('country', openapi.IN_QUERY, description="Country code ('kr' for Korea, 'us' for USA)", type=openapi.TYPE_STRING),
            openapi.Parameter('ticker', openapi.IN_QUERY, description="005930이나 AAPL 등의 ticker", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        country_str = request.query_params.get('country')
        ticker_str = request.query_params.get('ticker')
        if not country_str or not ticker_str:
            return Response({"error": "입력값이 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if country_str == "kr":
            country_str = "KR"
        elif country_str == "us":
            country_str = "EN"
        else:
            return Response({"error": "국가는 kr, us 두개만 받습니다."}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            formatted_today = today.strftime('%y%m%d')
            formatted_yesterday = yesterday.strftime('%y%m%d')

            session = boto3.Session(
                aws_access_key_id= os.getenv('ACCESS_KEY_ID'),
                aws_secret_access_key= os.getenv('SECRET_ACCESS_KEY'),
            )
            s3 = session.client('s3')

            if ticker_str.isdigit():
                csv_file_name = f"{country_str}_{int(ticker_str)}_temp.csv"
            else:
                csv_file_name = f"{country_str}_{ticker_str}_temp.csv"

            # 오늘부터 최대 10일 전까지의 폴더를 확인
            folders_to_try = []
            for i in range(10):
                date_to_check = today - timedelta(days=i)
                formatted_date = date_to_check.strftime('%y%m%d')
                folder_to_try = f"real_time/{formatted_date}_{country_str}_done"
                folders_to_try.append(folder_to_try)

            csv_obj = None

            for folder in folders_to_try:
                try:
                    file_key = f"{folder}/{csv_file_name}"
                    csv_obj = s3.get_object(Bucket='team-won-2-bucket', Key=file_key)
                    break  # 파일을 성공적으로 읽으면 루프를 종료
                except s3.exceptions.NoSuchKey:
                    continue  # 파일이 없으면 다음 폴더를 시도

            if csv_obj:
                # 파일을 읽어 데이터프레임으로 변환
                body = csv_obj['Body']
                csv_string = body.read().decode('utf-8')
                # CSV 파일을 헤더 없이 읽기
                df = pd.read_csv(io.StringIO(csv_string), header=None)
                # 열 이름을 수동으로 지정
                df.columns = ["title", "originallink", "link", "description", "pubDate"]
            else:
                return Response({"error": "오늘과 어제의 news 데이터가 없습니다.(수정가능)"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 데이터프레임을 JSON 형식으로 변환
            json_data = df.to_dict(orient='records')

            # JSON 형식으로 데이터 반환
            return Response(json_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)