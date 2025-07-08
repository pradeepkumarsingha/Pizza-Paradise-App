def cart_count(request):
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        count = sum(item['quantity'] for item in cart.values())
    else:
        count = 0
    return {'cart_count': count} 