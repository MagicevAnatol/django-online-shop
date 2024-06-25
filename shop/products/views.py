from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from .filters import ProductFilter


class CatalogListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


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