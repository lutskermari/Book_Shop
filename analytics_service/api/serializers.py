from rest_framework import serializers
from .models import SaleAnalytics

class SaleAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleAnalytics
        fields = ['id', 'book_id', 'book_title', 'quantity', 'total_price', 'created_at']