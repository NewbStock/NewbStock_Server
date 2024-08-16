from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),  # 앱의 루트 URL에 DRF 홈 화면 연결
    path('submit-data/', InvestmentDataView.as_view(), name='submit-data'),
    path('calculate-returns/', CalculateReturnsView.as_view(), name='calculate-returns'),
]
