from django.db import models


# Create your models here.
class SaleAnalytics(models.Model):
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=255)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book_title} - {self.quantity} шт."
