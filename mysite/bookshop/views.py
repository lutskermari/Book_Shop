from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book, Category
from django.db.models import Q, Count

# Create your views here.
def index(request):
    result = Book.objects.all()
    return render(request, "index.html", {'books': result})

def category_list(request):
    categories = Category.objects.annotate(books_count=Count('book', filter=Q(book__price__gt=300))).filter(books_count__gt=0)
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
            
        return queryset

class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_book = self.object
        context["previous_book"] = Book.objects.filter(id__lt=current_book.id).order_by("-id").first()
        context["next_book"] = Book.objects.filter(id__gt=current_book.id).order_by("id").first()

        return context

class BookCreateView(CreateView):
    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')

class BookUpdateView(UpdateView):
    model = Book
    template_name = "book_create.html"
    fields = ['title', 'author', 'category', 'price', 'published_date', 'description']
    success_url = reverse_lazy('index')

class BookDeleteView(DeleteView):
    model = Book
    template_name = "book_confirm_delete.html"
    success_url = reverse_lazy('index')