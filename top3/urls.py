from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),  # 앱의 루트 URL에 DRF 홈 화면 연결
]
