from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger Schema View 설정
schema_view = get_schema_view(
    openapi.Info(
        title="Newbstock API",
        default_version='v1',
        description="Newbstock API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# DefaultRouter 생성
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),  # 루트 URL에 DRF 기본 홈 화면 연결 (모든 엔드포인트)
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # 인증 엔드포인트
    path('profit/', include('profit.urls')),  # profit 앱의 URL 패턴 포함
    path('newb/', include('newb.urls')),  # newb 앱의 URL 패턴 포함
    path('top3/', include('top3.urls')),  # top3 앱의 URL 패턴 포함
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger 문서
]
