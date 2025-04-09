"""Admin configuration for the inventory app."""
from django.db import models
class Product(models.Model):
    """Handles inventory item operations."""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    low_stock_threshold = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name

class Order(models.Model):
    """Form for handling orders."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    customer_name = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product.name}"

class Report(models.Model):
    """Form for handling Report."""
    report_date = models.DateField()
    total_orders = models.IntegerField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.report_date)
