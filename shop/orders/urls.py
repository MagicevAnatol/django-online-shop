from django.urls import path

from .views import OrderAPIView, OrderDetailView, PaymentView, PaymentSomeoneView

app_name = 'orders'

urlpatterns = [
    path('orders', OrderAPIView.as_view(), name='order-list-create'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('payment/<int:pk>', PaymentView.as_view(), name='payment'),
    path('payment-someone/', PaymentSomeoneView.as_view(), name='payment-someone'),
]