from decimal import Decimal
from .models import Book


class Cart:
    def __init__(self, request):
        self.session = request.session
        if "cart" not in self.session:
            self.session["cart"] = {}
        self.cart = self.session["cart"]

    def add(self, book, quantity=1):
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {"quantity": 0, "price": str(book.price)}
        self.cart[book_id]["quantity"] += quantity
        self.session.modified = True

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.session.modified = True

    def clear(self):
        self.session["cart"] = {}
        self.session.modified = True

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):
        books = Book.objects.filter(id__in=self.cart.keys())
        books_map = {str(b.id): b for b in books}
        for book_id, item in self.cart.items():
            book = books_map.get(book_id)
            if book:
                yield {
                    "book": book,
                    "quantity": item["quantity"],
                    "price": Decimal(item["price"]),
                    "total_price": Decimal(item["price"]) * item["quantity"],
                }