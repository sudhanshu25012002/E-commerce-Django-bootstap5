from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import Profile, Cart, CartItems
from products.models import SizeVariant, Product, Coupon
import razorpay
from django.conf import settings

# Create your views here.
def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = email)
        if not user_obj.exists():
            messages.warning(request, 'Email is not registered')
            return HttpResponseRedirect(request.path_info)
        # is_email_varified
        if not user_obj[0].profile.is_email_varified:
            messages.warning(request, 'Email is not verified')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email, password = password)
        if user_obj:
            login(request, user_obj)
            return redirect('/')
            
        messages.warning(request, 'Invalid username or password')
        return HttpResponseRedirect(request.path_info)
    
    return render(request, 'accounts/login.html')


def register_page(request):
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = User.objects.create(first_name = first_name, last_name = last_name, email = email, username = email)
        user_obj.set_password(password)
        user_obj.save()
        
        messages.success(request, "An email has been sent on mail")
        return HttpResponseRedirect(request.path_info)
        
    return render(request, 'accounts/register.html')


def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token = email_token)
        user.is_email_varified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid email token')
                
                
def cart(request):
    cart_obj = Cart.objects.filter(is_paid = False, user = request.user)
    
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
        
        if not coupon_obj.exists():
            messages.warning(request, 'Invalid coupon code')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj.coupon:
            messages.warning(request, 'Coupon already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_amount:
            messages.warning(request, f'Amount should be greater than {coupon_obj[0].minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        if coupon_obj[0].is_expired:
            messages.warning(request, f'Coupon expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        
        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, 'Coupon applied successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))        

    client = razorpay.Client(auth= (settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    # payment = client.order.create({'amount': cart_obj[0].get_cart_total()*100, 'currency': 'INR', 'payment_capture': 1})

    context = {'cart': cart_obj}
    return render(request, 'accounts/cart.html', context)


def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    
    product = Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    cart_item = CartItems.objects.create(cart=cart, product=product)

    if variant:
        variant = request.GET.get('variant')
        size_variant = SizeVariant.objects.get(size_name = variant)
        cart_item.size_variant = size_variant
        cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_coupon(request, cart_uid):
    cart = Cart.objects.get(uid = cart_uid)
    cart.couopn = None
    cart.save()
    
    messages.success(request, 'Coupon Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   


def logout_user(request):
    logout(request)
    return redirect('index')


def get_cart_item_count(request):
      # Retrieve the cart item count for the current user
    test = 0
    cart_items_count = CartItems.objects.filter(cart__user=request.user, cart__is_paid=False).count()
    context =  {'cart_item_count': cart_items_count, 'test': test} # Pass the cart item count to the template context
    
    return render(request, 'base/base.html', context)
