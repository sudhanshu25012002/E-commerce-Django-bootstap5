from django.urls import path
from accounts.views import add_to_cart, login_page, register_page, activate_email, cart, remove_cart, remove_coupon, logout_user

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('activate/<email_token>/', activate_email, name='activate_email'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove-cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('remove-couopn/<cart_id>/', remove_coupon, name='remove_coupon'),
    path('logout/', logout_user, name='logout'),
]