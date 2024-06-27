from rest_framework import serializers
from .models import Category, Tag, Product, Review, Specification, Subcategory


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'image_src', 'image_alt']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_src', 'image_alt', 'subcategories']


class ImageSerializer(serializers.Serializer):
    src = serializers.CharField()
    alt = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date',]

    def create(self, validated_data):
        product_id = self.context['product_id']
        product = Product.objects.get(pk=product_id)
        return Review.objects.create(product=product, **validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, source='get_images')
    tags = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Tag.objects.all())
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    fullDescription = serializers.CharField(source='full_description')
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription',
                  'freeDelivery', 'images', 'tags', 'reviews', 'specifications', 'rating']


class CatalogProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, source='get_images')
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source='reviews.count')
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery',
                  'images', 'tags', 'reviews', 'rating']