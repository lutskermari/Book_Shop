from rest_framework import serializers
from .models import Category, Book, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='category'
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'description', 'published_date', 'stock', 'category', 'category_ids']


class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'price', 'quantity', 'get_cost']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.ReadOnlyField(source='get_total_cost')

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'paid', 'created_at', 'items', 'total_cost']


class CartItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)