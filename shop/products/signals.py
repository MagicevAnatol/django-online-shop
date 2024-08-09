from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem
from accounts.models import Profile


def move_cart_to_user(request, user, old_session_key):
    session_cart = Cart.objects.filter(session_key=old_session_key).first()
    print("Старая сессия:", old_session_key)
    print("Пользователь вошел, перенос корзины:", session_cart)

    if session_cart:
        profile = user.profile
        user_cart, created = Cart.objects.get_or_create(profile=profile)
        for item in session_cart.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart, product=item.product
            )
            if not created:
                cart_item.count += item.count
            cart_item.save()
        session_cart.delete()


@receiver(user_logged_in)
def move_cart_to_user_signal(sender, request, user, **kwargs):
    old_session_key = request.session.session_key
    move_cart_to_user(request, user, old_session_key)
