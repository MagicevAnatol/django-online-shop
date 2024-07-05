from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Category, Review, Tag, Cart, CartItem, Sale
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer, ProductDetailSerializer, \
    TagSerializer, BasketProductSerializer, SaleProductSerializer
from .filters import ProductFilter


class CatalogListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Извлечение параметров фильтрации
        tags = self.request.query_params.getlist('tags[]')
        sort = self.request.query_params.get('sort', 'date')
        name = self.request.query_params.get('filter[name]')
        sort_type = self.request.query_params.get('sortType', 'dec')
        min_price = self.request.query_params.get('filter[minPrice]', 0)
        max_price = self.request.query_params.get('filter[maxPrice]', 50000)
        free_delivery = self.request.query_params.get('filter[freeDelivery]', 'false')
        available = self.request.query_params.get('filter[available]', 'false')
        category_id = (self.request.query_params.get('category'))
        # Фильтрация по тегам
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()

        # Фильтрация по названию
        if name:
            queryset = queryset.filter(Q(title__icontains=name) | Q(description__icontains=name))

        # Фильтрация по цене
        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        # Фильтрация по наличию
        if available == 'true':
            queryset = queryset.filter(available=True)
        else:
            queryset = queryset.filter(available=False)

        # Фильтрация по бесплатной доставке
        if free_delivery == 'true':
            queryset = queryset.filter(free_delivery=True)
        else:
            queryset = queryset.filter(free_delivery=False)

        # Фильтрация по категории
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Сортировка
        if sort_type == 'dec':
            sort = '-' + sort
        return queryset.order_by(sort)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "items": serializer.data,
            "currentPage": request.query_params.get('page', 1),
            "lastPage": self.paginator.page.paginator.num_pages if self.paginator else 1
        })


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'subcategory').all()
    serializer_class = ProductDetailSerializer

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        instance.views += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductReviewView(APIView):

    def get(self, request, product_id):
        product = Product.objects.get(pk=product_id)
        reviews = Review.objects.select_related('product').filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        serializer = ReviewSerializer(data=request.data, context={'product_id': product_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PopularProductView(APIView):

    def get(self, request):
        popular_product = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').order_by(
            "-views", "-rating")[:8]
        serializer = ProductSerializer(popular_product, many=True)
        return Response(serializer.data)


class LimitedProductView(APIView):
    def get(self, request):
        limited_products = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').filter(
            limited=1)[:16]
        serializer = ProductSerializer(limited_products, many=True)
        return Response(serializer.data)


class TagsProductView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class BasketView(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            profile = request.user.profile
            cart = get_object_or_404(Cart, profile=profile)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart = get_object_or_404(Cart, session_key=session_key)

        products = [item.product for item in cart.items.all()]
        serializer = BasketProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('id')
        count = request.data.get('count', 1)
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            profile = request.user.profile
            cart, created = Cart.objects.get_or_create(profile=profile)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.count += count
        else:
            cart_item.count = count
        cart_item.save()

        products = [item.product for item in cart.items.all()]
        serializer = BasketProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        product_id = request.data.get('id')
        count = request.data.get('count', 1)
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            profile = request.user.profile
            cart = get_object_or_404(Cart, profile=profile)
        else:
            session_key = request.session.session_key
            cart = get_object_or_404(Cart, session_key=session_key)

        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        if cart_item.count > count:
            cart_item.count -= count
            cart_item.save()
        else:
            cart_item.delete()

        products = [item.product for item in cart.items.all()]
        serializer = BasketProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SaleProductView(APIView):

    def get(self, request):
        today = timezone.now().date()
        sales = Sale.objects.filter(date_from__lte=today, date_to__gte=today)
        serializer = SaleProductSerializer(sales, many=True)
        return Response({
            'items': serializer.data,
            'currentPage': 1,
            'lastPage': 1
        }, status=status.HTTP_200_OK)