from django.urls import path, include
from rest_framework.routers import DefaultRouter
from top3 import views


router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),  # 앱의 루트 URL에 DRF 홈 화면 연결
    path('top3/', views.s3newsgetView.as_view(), name='s3newsget'),
    path('ticker/', views.StockRankListView.as_view(), name='StockRankListView'),
]
