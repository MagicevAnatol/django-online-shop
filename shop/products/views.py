from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Category, Review, Tag
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer, CatalogProductSerializer, \
    TagSerializer
from .filters import ProductFilter


class CatalogListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = CatalogProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        sort = self.request.query_params.get('sort', 'date')
        sort_type = self.request.query_params.get('sortType', 'dec')

        if category_id:
            queryset = queryset.filter(category__id=category_id)

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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        instance.views += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductReviewView(APIView):

    def get(self, request, product_id):
        product = Product.objects.get(pk=product_id)
        reviews = Review.objects.filter(product=product)
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
        popular_product = Product.objects.all().order_by("-views", "-rating")[:8]
        serializer = ProductSerializer(popular_product, many=True)
        return Response(serializer.data)


class LimitedProductView(APIView):
    def get(self, request):
        limited_products = Product.objects.filter(limited=1)[:16]
        serializer = ProductSerializer(limited_products, many=True)
        return Response(serializer.data)


class TagsProductView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
