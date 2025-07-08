from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(PizzaCategory)
admin.site.register(Pizza)
admin.site.register(cart)
admin.site.register(cart_items)
admin.site.register(order)
admin.site.register(order_items)
admin.site.register(payment)


