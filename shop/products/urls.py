from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CatalogListView, CategoryListView, ProductViewSet, ProductReviewView

app_name = 'products'

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    path("", include(router.urls)),
    path('catalog', CatalogListView.as_view(), name='catalog'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('product/<int:product_id>/reviews', ProductReviewView.as_view(), name='product-reviews'),
]
