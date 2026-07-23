import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category_slug = django_filters.CharFilter(field_name="category__slug", lookup_expr='exact')

    class Meta:
        model = Book
        fields = ['stock', 'author']