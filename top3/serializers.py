from rest_framework import serializers
from .models import *

class StockRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRank
        fields = '__all__'