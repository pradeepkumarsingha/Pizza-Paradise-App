from django.db import models
from django.contrib.auth.models import User
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class PizzaCategory(BaseModel):
    category_name=models.CharField(max_length=100)

class Pizza(BaseModel):
    category=models.ForeignKey(PizzaCategory, on_delete=models.CASCADE,related_name='pizzas')
    name=models.CharField(max_length=100)
    price=models.DecimalField(default=100, decimal_places=2, max_digits=10)
    images=models.ImageField(upload_to='pizzas')

class cart(BaseModel):
    user=models.ForeignKey(User,null=True,blank=True ,on_delete=models.SET_NULL,related_name='carts')
    is_paid=models.BooleanField(default=False)
 

class cart_items(BaseModel):
    cart=models.ForeignKey(cart, on_delete=models.CASCADE,related_name='cart_items')
    pizza=models.ForeignKey(Pizza, on_delete=models.CASCADE,related_name='cart_items')

class order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    payment_status = models.BooleanField(default=False)

class order_items(BaseModel):
    order = models.ForeignKey(order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class payment(BaseModel):
    order = models.ForeignKey(order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

# Create your models here.
# Create your models here.
