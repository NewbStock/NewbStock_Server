from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_superset_charts(request):
    superset_charts = [
        {
            'name': 'Chart 1',
            'url': 'https://your-superset-url/superset/explore/?form_data=...1'
        },
        {
            'name': 'Chart 2',
            'url': 'https://your-superset-url/superset/explore/?form_data=...2'
        },
        {
            'name': 'Chart 3',
            'url': 'https://your-superset-url/superset/explore/?form_data=...3'
        },
        # 필요한 만큼 차트를 추가할 수 있습니다.
    ]
    
    # URL 리스트를 JSON 형태로 반환합니다.
    return Response({'superset_charts': superset_charts})