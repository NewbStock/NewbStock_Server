from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),  # 앱의 루트 URL에 DRF 홈 화면 연결
    path('stocktop3kr/', StockTop3KR.as_view(), name='stocktop3kr'),
    path('stocktop3us/', StockTop3US.as_view(), name='stocktop3us'),
    
]
