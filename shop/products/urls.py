from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CatalogListView, CategoryListView, ProductViewSet, ProductReviewView, PopularProductView, \
    LimitedProductView, TagsProductView, BasketView, SaleProductView, BannersView

app_name = 'products'

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    path("", include(router.urls)),
    path('catalog/', CatalogListView.as_view(), name='catalog'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('product/<int:product_id>/review', ProductReviewView.as_view(), name='product-reviews'),
    path("products/popular", PopularProductView.as_view(), name='product-popular'),
    path("products/limited", LimitedProductView.as_view(), name='product-limited'),
    path("tags/", TagsProductView.as_view(), name='tags'),
    path("basket", BasketView.as_view(), name='basket'),
    path("sales", SaleProductView.as_view(), name='sales'),
    path("banners", BannersView.as_view(), name='banners'),
]
