from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import Book, Category, Order, OrderItem
from django.db.models import Q, Count
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.decorators.http import require_POST
from .cart import Cart
from django.core.mail import send_mail
import logging
import stripe

logger = logging.getLogger("bookshop")

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    """
    Відображає головну сторінку каталогу книг.

    Отримує всі книги з бази даних та передає їх у шаблон.
    Логує кожне відвідування сторінки.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Відрендерений шаблон index.html зі списком книг.
    """
    result = Book.objects.all()
    logger.info(f"Головна | user: {request.user}")
    return render(request, "index.html", {'books': result})


def category_list(request):
    """
    Відображає список категорій з кількістю книг дорожче 300 грн.

    Використовує annotate та filter для отримання тільки тих категорій,
    які мають хоча б одну книгу дорожче 300 грн.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Відрендерений шаблон categories.html зі списком категорій.
    """
    categories = Category.objects.annotate(
        books_count=Count('book', filter=Q(book__price__gt=300))
    ).filter(books_count__gt=0)
    logger.info(f"Категорії | user: {request.user}")
    return render(request, "categories.html", {'categories': categories})


class BookListView(ListView):
    """
    Відображає список книг з можливістю пошуку.

    Підтримує пошук за назвою та автором через GET параметр 'search'.
    Використовує Q-об'єкти для комбінованого пошуку.

    Attributes:
        model: Модель Book.
        template_name: Шаблон book_list.html.
        context_object_name: Назва змінної в шаблоні.
    """

    model = Book
    template_name = "book_list.html"
    context_object_name = "book_list"

    def get_queryset(self):
        """
        Повертає queryset книг з урахуванням пошукового запиту.

        Returns:
            QuerySet: Відфільтрований список книг.
        """
        queryset = super().get_queryset()
        query = self.request.GET.get('search')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
            logger.info(f"Пошук: '{query}' | user: {self.request.user}")

        return queryset


class BookDetailView(DetailView):
    """
    Відображає детальну сторінку книги.

    Додає в контекст попередню та наступну книги для навігації.

    Attributes:
        model: Модель Book.
        template_name: Шаблон book_detail.html.
        context_object_name: Назва змінної в шаблоні.
        pk_url_kwarg: Назва параметра URL для pk.
    """

    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        """
        Додає previous_book та next_book в контекст шаблону.

        Returns:
            dict: Контекст з даними книги та сусідніми книгами.
        """
        context = super().get_context_data(**kwargs)
        logger.info(f"Книга: '{self.object.title}' | user: {self.request.user}")
        current_book = self.object
        context["previous_book"] = Book.objects.filter(
            id__lt=current_book.id
        ).order_by("-id").first()
        context["next_book"] = Book.objects.filter(
            id__gt=current_book.id
        ).order_by("id").first()
        return context


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Створює нову книгу в каталозі.

    Доступно тільки авторизованим користувачам з правом bookshop.add_book.
    Після успішного створення перенаправляє на головну сторінку.

    Attributes:
        permission_required: Право необхідне для доступу.
    """

    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')
    permission_required = 'bookshop.add_book'

    def form_valid(self, form):
        """
        Зберігає книгу та логує створення.

        Args:
            form: Валідна форма з даними книги.

        Returns:
            HttpResponse: Перенаправлення на success_url.
        """
        logger.info(f"Створено книгу: '{form.instance.title}' | user: {self.request.user}")
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Редагує існуючу книгу в каталозі.

    Доступно тільки авторизованим користувачам з правом bookshop.change_book.

    Attributes:
        permission_required: Право необхідне для доступу.
    """

    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')
    permission_required = 'bookshop.change_book'

    def form_valid(self, form):
        """
        Зберігає зміни та логує оновлення.

        Args:
            form: Валідна форма з оновленими даними.

        Returns:
            HttpResponse: Перенаправлення на success_url.
        """
        logger.info(f"Оновлено книгу: '{form.instance.title}' | user: {self.request.user}")
        return super().form_valid(form)


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Видаляє книгу з каталогу.

    Доступно тільки авторизованим користувачам з правом bookshop.delete_book.
    Логує видалення на рівні WARNING.

    Attributes:
        permission_required: Право необхідне для доступу.
    """

    model = Book
    template_name = "book_confirm_delete.html"
    success_url = reverse_lazy('index')
    permission_required = 'bookshop.delete_book'

    def form_valid(self, form):
        """
        Видаляє книгу та логує операцію.

        Args:
            form: Форма підтвердження видалення.

        Returns:
            HttpResponse: Перенаправлення на success_url.
        """
        logger.warning(f"Видалено книгу: '{self.object.title}' | user: {self.request.user}")
        return super().form_valid(form)


@require_POST
def cart_add(request, book_id):
    """
    Додає книгу в кошик.

    Приймає тільки POST запити. Повертає 404 якщо книга не існує.

    Args:
        request: HTTP запит з полем quantity.
        book_id: ID книги яку треба додати.

    Returns:
        HttpResponseRedirect: Перенаправлення на сторінку кошика.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(book=book, quantity=quantity)
    return redirect("cart_detail")


@require_POST
def cart_remove(request, book_id):
    """
    Видаляє книгу з кошика.

    Приймає тільки POST запити. Повертає 404 якщо книга не існує.

    Args:
        request: HTTP запит.
        book_id: ID книги яку треба видалити.

    Returns:
        HttpResponseRedirect: Перенаправлення на сторінку кошика.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect("cart_detail")


def cart_clear(request):
    """
    Очищає весь кошик.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponseRedirect: Перенаправлення на сторінку кошика.
    """
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


def cart_detail(request):
    """
    Відображає вміст кошика.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Відрендерений шаблон cart_detail.html.
    """
    cart = Cart(request)
    return render(request, "cart_detail.html", {"cart": cart})


def order_create(request):
    """
    Створює замовлення з товарів кошика та ініціює оплату через Stripe.

    Використовує transaction.atomic для цілісності даних.
    Stripe сесія створюється ПОЗА транзакцією щоб уникнути
    невідповідності між БД та платіжною системою.

    Args:
        request: HTTP запит з даними форми (POST) або порожній (GET).

    Returns:
        HttpResponseRedirect: Перенаправлення на Stripe Checkout (303).
        HttpResponse: Форма замовлення (GET).
    """
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
            logger.info(f"Замовлення #{order.id} створено | user: {request.user}")

        payment_url = create_payment_session(request, order)
        cart.clear()
        return redirect(payment_url, code=303)

    return render(request, "order_create.html", {"cart": cart})


def create_payment_session(request, order):
    """
    Створює Stripe Checkout Session для оплати замовлення.

    Args:
        request: HTTP запит для побудови абсолютних URL.
        order: Об'єкт Order для якого створюється сесія оплати.

    Returns:
        str: URL сторінки оплати Stripe.
    """
    success_url = request.build_absolute_uri(
        reverse('order_success') + f"?order_id={order.id}"
    )
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
    """
    Обробляє успішну оплату замовлення.

    Захищає від подвійної обробки через перевірку order.paid.
    Відправляє email підтвердження тільки при першому виклику.

    Args:
        request: HTTP запит з параметром order_id в GET.

    Returns:
        HttpResponse: Відрендерений шаблон order_success.html.
    """
    order = get_object_or_404(Order, id=request.GET.get('order_id'))

    if not order.paid:
        order.paid = True
        order.save()
        logger.info(f"Замовлення #{order.id} оплачено")
        send_mail(
            subject=f"Замовлення #{order.id} успішно оплачено!",
            message=f"Дякуємо за оплату замовлення на суму {order.get_total_cost()} грн.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.email],
        )

    return render(request, "order_success.html", {"order": order})