from django.contrib import admin
from django import forms

from .models import Category, Subcategory, Tag, Product, Specification, Review, Image


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }


class ReviewInline(admin.TabularInline):
    form = ReviewForm
    model = Review
    extra = 1


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'price', 'count', 'date', 'free_delivery', 'rating')
    search_fields = ('title', 'description', 'full_description')
    list_filter = ('category', 'subcategory', 'tags', 'free_delivery', 'date')
    inlines = [ImageInline, SpecificationInline, ReviewInline]
    fieldsets = (
        (None, {
            'fields': (
                'title', 'category', 'subcategory', 'description', 'full_description', 'price', 'count',
                'views', 'free_delivery',
                'tags', 'rating'
            )
        }),
    )


class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubcategoryInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory)
admin.site.register(Tag)
admin.site.register(Product, ProductAdmin)
