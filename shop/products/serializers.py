from rest_framework import serializers
from .models import Category, Tag, Product, Review, Specification, Subcategory, Image, CartItem, Cart, Sale


class SubcategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'image']

    def get_image(self, obj):
        return {
            "src": obj.image_src.url if obj.image_src else "",
            "alt": obj.image_alt if obj.image_alt else "",
        }


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'subcategories']

    def get_image(self, obj):
        return {
            "src": obj.image_src.url if obj.image_src else "",
            "alt": obj.image_alt if obj.image_alt else "",
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('src', 'alt')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date', ]

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


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Tag.objects.all())
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    fullDescription = serializers.CharField(source='full_description')
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription',
                  'freeDelivery', 'images', 'tags', 'reviews', 'specifications', 'rating']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source='reviews.count')
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery',
                  'images', 'tags', 'reviews', 'rating']


class BasketProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source='reviews.count')
    freeDelivery = serializers.BooleanField(source='free_delivery')
    count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery',
                  'images', 'tags', 'reviews', 'rating']

    def get_count(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            profile = request.user.profile
            cart_item = CartItem.objects.filter(cart__profile=profile, product=obj).first()
        else:
            session_key = request.session.session_key
            cart_item = CartItem.objects.filter(cart__session_key=session_key, product=obj).first()

        if cart_item:
            return cart_item.count
        return 0


class SaleProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product_id")
    price = serializers.IntegerField(source='product.price', read_only=True)
    salePrice = serializers.IntegerField(source='sale_price')
    dateFrom = serializers.DateField(format='%m-%d', source='date_from')
    dateTo = serializers.DateField(format='%m-%d', source='date_to')
    title = serializers.CharField(source='product.title', read_only=True)
    images = serializers.SerializerMethodField()
    class Meta:
        model = Sale
        fields = ['id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images']

    def get_images(self, obj):
        images = Image.objects.filter(product_id=obj.product_id)
        return [{"src": image.src.url, "alt": image.alt} for image in images]