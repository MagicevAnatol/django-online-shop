from django.contrib import admin
from .models import Category, Tag, Product, Specification, Review


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'count', 'date', 'free_delivery', 'rating')
    search_fields = ('title', 'description', 'full_description')
    list_filter = ('category', 'tags', 'free_delivery', 'date')
    inlines = [SpecificationInline, ReviewInline]
    fieldsets = (
        (None, {
            'fields': (
                'title', 'category', 'description', 'full_description', 'price', 'count', 'free_delivery', 'tags',
                'rating')
        }),
        ('Images', {
            'fields': ('product_src', 'product_alt')
        }),
    )


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Product, ProductAdmin)
