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