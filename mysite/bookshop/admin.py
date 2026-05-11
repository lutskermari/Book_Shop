from django.contrib import admin
from .models import Book, Category

# Register your models here.
class BookInline(admin.TabularInline):
    model = Book.category.through 
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',) 
    inlines = [BookInline]   

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock')
    search_fields = ('title', 'author') 
    list_filter = ('stock', 'category') 