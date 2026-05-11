from django.shortcuts import render
from .models import Book, Category
from django.db.models import Q, Count

# Create your views here.
def index(request):
    result = Book.objects.all()
    return render(request, "catalog/index.html", {'books': result})

def category_list(request):
    categories = Category.objects.annotate(books_count = Count('book', filter=Q(book__price__gt=300))).filter(books_count__gt=0)
    return render(request, "catalog/categories.html", {'categories': categories})