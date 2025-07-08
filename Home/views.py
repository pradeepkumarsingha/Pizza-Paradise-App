from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import Pizza, cart as CartModel, order as OrderModel, payment as PaymentModel, order_items as OrderItemModel
import uuid
import paypalrestsdk
from django.urls import reverse
import json

# Initialize PayPal with proper configuration
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
    "verify_ssl": True  # Enable SSL verification
})

# Create your views here.
def home(request):
    featured_pizzas = Pizza.objects.all()[:3]  # Get first 3 pizzas as featured
    return render(request, 'home.html', {'featured_pizzas': featured_pizzas})

def menu(request):
    pizzas = Pizza.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        pizzas = pizzas.filter(
            name__icontains=search_query
        ) | pizzas.filter(
            description__icontains=search_query
        )
    
    context = {
        'pizzas': pizzas,
        'search_query': search_query
    }
    return render(request, 'menu.html', context)

def cart(request):
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to view your cart')
        return redirect('login')
    
    try:
        user_cart = CartModel.objects.get(is_paid=False, user=request.user)
    except CartModel.DoesNotExist:
        user_cart = None
        
    cart_items = []
    total = 0
    payment_url = None
    
    # Get items from session cart
    session_cart = request.session.get('cart', {})
    for pizza_id, item in session_cart.items():
        try:
            pizza = Pizza.objects.get(id=pizza_id)
            item_total = float(item['price']) * item['quantity']
            total += item_total
            cart_items.append({
                'pizza': pizza,
                'quantity': item['quantity'],
                'total': item_total
            })
        except Pizza.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'user_cart': user_cart
    }
    
            
    
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, 'Your cart is empty')
            return redirect('menu')
        
        cart_items = []
        total = 0
        
        for pizza_id, item in cart.items():
            try:
                pizza = Pizza.objects.get(id=pizza_id)
                item_total = float(item['price']) * item['quantity']
                total += item_total
                cart_items.append({
                    'pizza': pizza,
                    'quantity': item['quantity'],
                    'total': item_total
                })
            except Pizza.DoesNotExist:
                continue
        
        if total > 0:
            try:
                # Create order
                order = OrderModel.objects.create(
                    user=request.user,
                    total_amount=total,
                    status='pending',
                    payment_status=False
                )
                
                # Create order items
                for item in cart_items:
                    OrderItemModel.objects.create(
                        order=order,
                        pizza=item['pizza'],
                        quantity=item['quantity'],
                        price=item['total']
                    )
                
                # Format total for PayPal (ensure it's a string with 2 decimal places)
                formatted_total = "{:.2f}".format(float(total))
                
                # Create PayPal payment with minimal required fields
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(reverse('payment_success')),
                        "cancel_url": request.build_absolute_uri(reverse('cart'))
                    },
                    "transactions": [{
                        "amount": {
                            "total": formatted_total,
                            "currency": "USD"
                        },
                        "description": f"Order #{order.id}"
                    }]
                })
                
                print("Creating PayPal payment with total:", formatted_total)
                
                if payment.create():
                    print("Payment created successfully:", payment.id)
                    
                    # Store IDs in session
                    request.session['paypal_payment_id'] = payment.id
                    request.session['order_id'] = str(order.id)
                    
                    # Create payment record
                    PaymentModel.objects.create(
                        order=order,
                        amount=total,
                        payment_method='PayPal',
                        status='pending',
                        transaction_id=payment.id
                    )
                    
                    # Get approval URL
                    approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
                    if approval_url:
                        return redirect(approval_url)
                    else:
                        raise Exception("No approval URL found in PayPal response")
                
                print("Payment creation failed:", payment.error)
                order.delete()
                messages.error(request, 'Could not initialize PayPal payment. Please try again.')
                
            except Exception as e:
                print("Checkout error:", str(e))
                if 'order' in locals():
                    order.delete()
                messages.error(request, 'Payment initialization failed. Please try again.')
                return redirect('cart')
    
    # GET request - show checkout page
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for pizza_id, item in cart.items():
        try:
            pizza = Pizza.objects.get(id=pizza_id)
            item_total = float(item['price']) * item['quantity']
            total += item_total
            cart_items.append({
                'pizza': pizza,
                'quantity': item['quantity'],
                'total': item_total
            })
        except Pizza.DoesNotExist:
            continue
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def payment_success(request):
    payment_id = request.session.get('paypal_payment_id')
    order_id = request.session.get('order_id')
    
    if not payment_id or not order_id:
        messages.error(request, 'Payment information not found')
        return redirect('cart')
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        order = OrderModel.objects.get(id=order_id)
        
        if payment.execute({"payer_id": request.GET.get('PayerID')}):
            # Update order status
            order.status = 'completed'
            order.payment_status = True
            order.save()
            
            # Update payment record
            payment_record = PaymentModel.objects.get(order=order)
            payment_record.status = 'completed'
            payment_record.save()
            
            # Clear cart and payment info from session
            request.session['cart'] = {}
            request.session['paypal_payment_id'] = None
            request.session['order_id'] = None
            request.session.modified = True
            
            messages.success(request, 'Payment successful! Your order has been placed.')
            return redirect('home')
        else:
            print("Payment execution failed:", payment.error)
            messages.error(request, 'Payment failed. Please try again.')
            
    except Exception as e:
        print("Error processing payment:", str(e))
        messages.error(request, 'Error processing payment. Please try again.')
    
    return redirect('cart')

def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.error(request, 'User does not exist')
                return redirect('login')
            
            user_obj = authenticate(username=username, password=password)
            if user_obj is None:
                messages.error(request, 'Invalid password')
                return redirect('login')
            
            auth_login(request, user_obj)
            messages.success(request, 'Login successful')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error logging in: {str(e)}')
            return redirect('login')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not username or not password:
                messages.error(request, 'Please fill in all fields')
                return redirect('register')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, 'Account created successfully')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register')
    return render(request, 'register.html')
            
 

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def add_to_cart(request, pizza_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to add items to cart')
        return redirect('login')
        
    try:
        pizza_id = uuid.UUID(pizza_id)
        pizza = get_object_or_404(Pizza, id=pizza_id)
    except (ValueError, Pizza.DoesNotExist):
        messages.error(request, 'Invalid pizza selected')
        return redirect('menu')
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    
    # Add pizza to cart or increment quantity
    if str(pizza_id) in cart:
        cart[str(pizza_id)]['quantity'] += 1
    else:
        cart[str(pizza_id)] = {
            'name': pizza.name,
            'price': str(pizza.price),
            'quantity': 1
        }
    
    request.session.modified = True
    messages.success(request, f'{pizza.name} added to cart!')

    return redirect('cart')

def remove_from_cart(request, pizza_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to manage your cart')
        return redirect('login')
        
    try:
        pizza_id = uuid.UUID(pizza_id)
        pizza = get_object_or_404(Pizza, id=pizza_id)
    except (ValueError, Pizza.DoesNotExist):
        messages.error(request, 'Invalid pizza selected')
        return redirect('cart')
        
    cart = request.session.get('cart', {})
    if str(pizza_id) in cart:
        del cart[str(pizza_id)]
        request.session.modified = True
        messages.success(request, f'{pizza.name} removed from cart')
    
    return redirect('cart')

@login_required
def profile(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, 'Email updated successfully')
            return redirect('checkout')
        else:
            messages.error(request, 'Please provide a valid email address')
    
    return render(request, 'profile.html', {'user': request.user})

# def payment(request):
