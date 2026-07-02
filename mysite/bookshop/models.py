from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")

    def __str__(self):
        return self.name

class Book(models.Model):
    category = models.ManyToManyField(Category, verbose_name="Category")
    title = models.CharField(max_length=100, verbose_name="Book Title")
    author = models.CharField(max_length=200, verbose_name="Author")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    description = models.TextField(verbose_name="Description")
    published_date = models.DateField(null=True, blank=True, verbose_name="Published Date")
    stock = models.BooleanField(default=True, verbose_name="Stock Status")

class Order(models.Model):
    first_name = models.CharField("Ім'я", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    email = models.EmailField("Email")
    address = models.CharField("Адреса", max_length=255)
    paid = models.BooleanField("Оплачено", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Замовлення #{self.id}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def get_cost(self):
        return self.price * self.quantity