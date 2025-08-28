from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
   
    phone = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return self.username


class Product(models.Model):
    
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    description = models.TextField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    delivery_fee =models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    photo = models.ImageField(upload_to="products/")  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def discount_percentage(self):
        
        if self.original_price > 0:
            return round(((self.original_price - self.selling_price) / self.original_price) * 100, 2)
        return 0

    def __str__(self):
        return f"{self.name} ({self.brand})"

