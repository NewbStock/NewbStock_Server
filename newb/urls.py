from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),  # 앱의 루트 URL에 DRF 홈 화면 연결
    path('stocktopkr/', StockTop3View.as_view(), name='StockTop3View'),
    path('highchange/', HighChangeStock.as_view(), name='HighChangeStock'),
]
