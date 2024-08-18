from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.views.generic import TemplateView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('stocktopkr/', StockTop3View.as_view(), name='StockTop3View'),
    path('highchange/', HighChangeStock.as_view(), name='HighChangeStock'),
    path('charts/', TemplateView.as_view(template_name='charts.html'), name='charts'),
    path('exchange/',ExchangeRateChartView.as_view(), name='ExchangeRateChartView'),
    path('kospi/',KospiKosdaqChartView.as_view(), name='KospiChartView'),
    path('interestrates/',InterestRateChartView.as_view(), name='InterestRatesChartView'),
    path('newssentiment/',NewsSentimentChartView.as_view(), name='NewsSentimentChartView'),
]

