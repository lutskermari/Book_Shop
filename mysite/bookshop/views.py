from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book, Category
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import logging

logger = logging.getLogger("bookshop")

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