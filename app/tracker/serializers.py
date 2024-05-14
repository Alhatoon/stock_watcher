from rest_framework import serializers
from .models import TrackingRecord

class TrackingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRecord
        fields = '__all__'
##