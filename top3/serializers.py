from rest_framework import serializers
from .models import StockRank

class StockRankSerializer(serializers.ModelSerializer):
    ticker = serializers.SerializerMethodField()

    class Meta:
        model = StockRank
        fields = '__all__'

    def get_ticker(self, obj):
        if obj.ticker.isdigit():
            return f"{int(obj.ticker):06d}"  # 숫자로 변환 후 6자리로 포맷
        return obj.ticker