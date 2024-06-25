import django_filters
from .models import Product, Tag


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    free_delivery = django_filters.BooleanFilter(field_name="free_delivery")
    available = django_filters.BooleanFilter(field_name="count", lookup_expr='gt', method='filter_available')
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'free_delivery', 'tags', 'available']

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(count__gt=0)
        return queryset
