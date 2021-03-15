from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    picture = models.FileField(upload_to='product_img/', blank=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def price(self):
        return self.product.price * self.quantity


class CaUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
