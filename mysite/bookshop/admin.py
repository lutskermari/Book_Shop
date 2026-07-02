from django.contrib import admin
from .models import Book, Category, Order, OrderItem

# Register your models here.
class BookInline(admin.TabularInline):
    model = Book.category.through 
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['book']
    extra = 0 

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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'created_at', 'paid']
    list_filter = ['paid', 'created_at']
    inlines = [OrderItemInline]