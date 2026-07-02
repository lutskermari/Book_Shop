from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import Book, Category, Order, OrderItem
from django.db.models import Q, Count
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .cart import Cart
from django.core.mail import send_mail
import logging
import stripe

logger = logging.getLogger("bookshop")

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
    result = Book.objects.all()
    logger.info(f"Головна | user: {request.user}")
    return render(request, "index.html", {'books': result})

def category_list(request):
    categories = Category.objects.annotate(books_count=Count('book', filter=Q(book__price__gt=300))).filter(books_count__gt=0)
    logger.info(f"Категорії | user: {request.user}")
    return render(request, "categories.html", {'categories': categories})

class BookListView(ListView):
    model = Book
    template_name = "book_list.html"
    context_object_name = "book_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
            logger.info(f"Пошук: '{query}' | user: {self.request.user}")

        return queryset

class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f"Книга: '{self.object.title}' | user: {self.request.user}")
        current_book = self.object
        context["previous_book"] = Book.objects.filter(id__lt=current_book.id).order_by("-id").first()
        context["next_book"] = Book.objects.filter(id__gt=current_book.id).order_by("id").first()

        return context

class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')

    permission_required = 'bookshop.add_book'

    def form_valid(self, form):
        logger.info(f"Створено книгу: '{form.instance.title}' | user: {self.request.user}")
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')

    permission_required = 'bookshop.change_book'

    def form_valid(self, form):
        logger.info(f"Оновлено книгу: '{form.instance.title}' | user: {self.request.user}")
        return super().form_valid(form)

class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = "book_confirm_delete.html"
    success_url = reverse_lazy('index')
    
    permission_required = 'bookshop.delete_book'

    def form_valid(self, form):
        logger.warning(f"Видалено книгу: '{self.object.title}' | user: {self.request.user}")
        return super().form_valid(form)
    
def cart_add(request, book_id):
    cart = Cart(request)
    book = Book.objects.get(id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(book=book, quantity=quantity)
    return redirect("cart_detail")

def cart_remove(request, book_id):
    cart = Cart(request)
    book = Book.objects.get(id=book_id)
    cart.remove(book)
    return redirect("cart_detail")

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart_detail.html", {"cart": cart})

def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('cart_detail')

    if request.method == "POST":
        with transaction.atomic():
            order = Order.objects.create(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                address=request.POST["address"],
            )
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item["book"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            payment_url = create_payment_session(request, order)

        cart.clear()

        return redirect(payment_url, code=303)

    return render(request, "order_create.html", {"cart": cart})

def create_payment_session(request, order):
    success_url = request.build_absolute_uri(reverse('order_success') + f"?order_id={order.id}")
    cancel_url = request.build_absolute_uri(reverse('cart_detail'))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"], 
        line_items=[
            {
                "price_data": {
                    "currency": "uah", 
                    "product_data": {
                        "name": f"Оплата замовлення #{order.id}",
                    },
                    "unit_amount": int(float(order.get_total_cost()) * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
    )
    return session.url 

def order_success(request):
    order = Order.objects.get(id=request.GET.get('order_id'))
    
    order.paid = True
    order.save()
    
    send_mail(
        subject=f"Замовлення #{order.id} успішно оплачено!",
        message=f"Дякуємо за оплату замовлення на суму {order.get_total_cost()} грн.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email],
    )
    
    return render(request, "order_success.html", {"order": order})