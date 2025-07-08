from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Home'


def ready(self):
    from django.contrib.auth.models import User
    def get_cart_count(self):
        from.models import CartItems
        cart_items=CartItems.objects.filter(cart=self,is_paid=False).count()
        return cart_items
    User.add_to_class('get_cart_count', get_cart_count)
