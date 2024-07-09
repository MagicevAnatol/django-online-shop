from django.urls import path

from .views import OrderAPIView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('orders', OrderAPIView.as_view(), name='order-list-create'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
]