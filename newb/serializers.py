from rest_framework import serializers
from .models import *

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = '__all__'

class KospiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kospi
        fields = '__all__'

class newssentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = newssentiment
        fields = '__all__'

class InterestRatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRates
        fields = '__all__'

class HighKRSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighKR
        fields = '__all__'

class HighUSASerializer(serializers.ModelSerializer):
    class Meta:
        model = HighUS
        fields = '__all__'

class StockKRTop100Serializer(serializers.ModelSerializer):
    class Meta:
        model = StockKRTop100
        fields = '__all__'

class StockUSTop100Serializer(serializers.ModelSerializer):
    class Meta:
        model = StockUSTop100
        fields = '__all__'


