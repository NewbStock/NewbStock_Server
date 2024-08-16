from rest_framework import serializers
from .models import *

class USTOP100Serializer(serializers.ModelSerializer):
    class Meta:
        model = USTOP100
        fields = '__all__'

class KRTOP100Serializer(serializers.ModelSerializer):
    class Meta:
        model = KRTOP100
        fields = '__all__'

class KRSTOCKDATASerializer(serializers.ModelSerializer):
    class Meta:
        model = KRSTOCKDATA
        fields = '__all__'

class USSTOCKDATASerializer(serializers.ModelSerializer):
    class Meta:
        model = USSTOCKDATA
        fields = '__all__'


class InvestmentCalculationSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=2)
    company = serializers.CharField(max_length=100)
    initial_amount = serializers.IntegerField()
    initial_date = serializers.DateField()
    additional_amount = serializers.IntegerField(required=False, default=0)
    frequency = serializers.ChoiceField(choices=["weekly", "biweekly", "monthly", "bimonthly"])