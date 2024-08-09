from django.db.models import Q, Count, Sum, QuerySet
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
    """
    Список товаров с фильтрацией, сортировкой и пагинацией.
    """
    queryset = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_queryset(self) -> QuerySet[Product]:
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags[]')
        sort = self.request.query_params.get('sort', 'date')
        name = self.request.query_params.get('filter[name]')
        sort_type = self.request.query_params.get('sortType', 'dec')
        min_price = float(self.request.query_params.get('filter[minPrice]', 0))
        max_price = float(self.request.query_params.get('filter[maxPrice]', 50000))
        free_delivery = self.request.query_params.get('filter[freeDelivery]', 'false')
        available = self.request.query_params.get('filter[available]', 'false')
        category_id = self.request.query_params.get('category')

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

        # Фильтрация по бесплатной доставке
        if free_delivery == 'true':
            queryset = queryset.filter(free_delivery=True)

        # Фильтрация по категории
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Сортировка
        if sort == 'reviews':
            queryset = queryset.annotate(review_count=Count('reviews'))
            sort = 'review_count'
        if sort_type == 'dec':
            sort = '-' + sort

        return queryset.order_by(sort)

    def list(self, request, *args, **kwargs) -> Response:
        limit = int(request.query_params.get('limit', 20))
        current_page = int(request.query_params.get('currentPage', 1))
        offset = (current_page - 1) * limit
        end = offset + limit

        queryset = self.filter_queryset(self.get_queryset())
        total_items = queryset.count()
        queryset = queryset[offset:end]

        serializer = self.get_serializer(queryset, many=True)
        last_page = (total_items + limit - 1) // limit

        return Response({
            "items": serializer.data,
            "currentPage": current_page,
            "lastPage": last_page
        })


class CategoryListView(generics.ListAPIView):
    """
    Список категорий с подкатегориями.
    """
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Управление товарами, включая просмотр деталей и увеличение количества просмотров.
    """
    queryset = Product.objects.select_related('category', 'subcategory').all()
    serializer_class = ProductDetailSerializer

    def retrieve(self, request, pk=None, **kwargs) -> Response:
        instance = self.get_object()
        instance.views += 1
        instance.save()
        today = timezone.now().date()
        active_sale = Sale.objects.filter(product=instance, date_from__lte=today, date_to__gte=today).first()
        if active_sale:
            instance.price = active_sale.sale_price
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductReviewView(APIView):
    """
    Получение и создание отзывов для товара.
    """

    def get(self, request, product_id: int) -> Response:
        product = Product.objects.get(pk=product_id)
        reviews = Review.objects.select_related('product').filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_id: int) -> Response:
        serializer = ReviewSerializer(data=request.data, context={'product_id': product_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PopularProductView(APIView):
    """
    Получение популярных товаров (по количеству просмотров и рейтингу).
    """

    def get(self, request) -> Response:
        popular_product = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').order_by(
            "-views", "-rating")[:8]
        serializer = ProductSerializer(popular_product, many=True)
        return Response(serializer.data)


class LimitedProductView(APIView):
    """
    Получение товаров с ограниченным количеством.
    """

    def get(self, request) -> Response:
        limited_products = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').filter(
            limited=1)[:16]
        serializer = ProductSerializer(limited_products, many=True)
        return Response(serializer.data)


class TagsProductView(APIView):
    """
    Получение популярных тегов (по количеству просмотров товаров с этими тегами).
    """

    def get(self, request) -> Response:
        tags = Tag.objects.annotate(total_views=Sum('product__views')).order_by('-total_views')[:10]
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class BasketView(APIView):
    """
    Управление корзиной пользователя (добавление, удаление товаров).
    """

    def get_cart(self, request) -> Cart:
        if request.user.is_authenticated:
            profile = request.user.profile
            cart = get_object_or_404(Cart, profile=profile)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def get(self, request) -> Response:
        cart = self.get_cart(request)
        products = [item.product for item in cart.items.all()]
        serializer = BasketProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        product_id = request.data.get('id')
        count = request.data.get('count', 1)
        product = get_object_or_404(Product, id=product_id)

        cart = self.get_cart(request)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.count += count
        else:
            cart_item.count = count
        cart_item.save()

        products = [item.product for item in cart.items.all()]
        serializer = BasketProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request) -> Response:
        product_id = request.data.get('id')
        count = request.data.get('count', 1)
        product = get_object_or_404(Product, id=product_id)

        cart = self.get_cart(request)

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
    """
    Получение товаров со скидками с поддержкой пагинации.
    """

    def get(self, request) -> Response:
        limit = 12
        current_page = int(request.query_params.get('currentPage', 1))
        offset = (current_page - 1) * limit
        end = offset + limit

        today = timezone.now().date()
        sales = Sale.objects.filter(date_from__lte=today, date_to__gte=today).prefetch_related('product')
        total_items = sales.count()
        sales = sales[offset:end]

        serializer = SaleProductSerializer(sales, many=True)
        last_page = (total_items + limit - 1) // limit

        return Response({
            'items': serializer.data,
            'currentPage': current_page,
            'lastPage': last_page
        }, status=status.HTTP_200_OK)


class BannersView(APIView):
    """
    Получение последних добавленных товаров для баннеров.
    """

    def get(self, request) -> Response:
        limited_products = Product.objects.select_related('category', 'subcategory').prefetch_related('tags').order_by(
            "-date")[:4]
        serializer = ProductSerializer(limited_products, many=True)
        return Response(serializer.data)