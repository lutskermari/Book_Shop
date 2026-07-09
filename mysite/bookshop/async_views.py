import asyncio
from django.http import JsonResponse
from django.db.models import Q
from asgiref.sync import sync_to_async

async def async_book_list(request):
    from .models import Book

    query = request.GET.get("search", "")
    queryset = Book.objects.order_by("title")

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    books = []
    async for book in queryset:
        books.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "price": str(book.price),
            "stock": book.stock,
        })

    return JsonResponse({"books": books, "count": len(books)})

async def async_book_detail(request, pk):
    from .models import Book

    try:
        book = await Book.objects.aget(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Книгу не знайдено"}, status=404)

    return JsonResponse({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": str(book.price),
        "description": book.description,
        "stock": book.stock,
        "category": book.category.name if book.category else None,
    })

async def async_catalog_stats(request):
    from .models import Book, Category
    import asyncio

    books_count, available_count, categories_count = await asyncio.gather(
        Book.objects.acount(),
        Book.objects.filter(stock=True).acount(),
        Category.objects.acount(),
    )

    from asgiref.sync import sync_to_async

    @sync_to_async
    def get_avg_price():
        from django.db.models import Avg
        result = Book.objects.aggregate(avg_price=Avg("price"))
        return str(round(result["avg_price"] or 0, 2))

    avg_price = await get_avg_price()

    return JsonResponse({
        "books_total": books_count,
        "books_available": available_count,
        "categories_total": categories_count,
        "avg_price": avg_price,
    })