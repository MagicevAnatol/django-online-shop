from django.contrib import admin
from django import forms

from .models import (
    Category,
    Subcategory,
    Tag,
    Product,
    Specification,
    Review,
    Image,
    Sale,
)


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = "__all__"
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "cols": 40}),
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
    list_display = (
        "title",
        "category",
        "subcategory",
        "price",
        "count",
        "date",
        "limited",
        "free_delivery",
        "available",
        "rating",
    )
    search_fields = ("title", "description", "full_description")
    list_filter = ("category", "subcategory", "tags", "free_delivery", "date")
    inlines = [ImageInline, SpecificationInline, ReviewInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "category",
                    "subcategory",
                    "description",
                    "full_description",
                    "price",
                    "count",
                    "views",
                    "free_delivery",
                    "limited",
                    "available",
                    "tags",
                    "rating",
                )
            },
        ),
    )


class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubcategoryInline]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "sale_price", "date_from", "date_to", "is_active")
    list_filter = ("date_from", "date_to")
    search_fields = ("product__title",)

    def is_active(self, obj):
        return obj.is_active()

    is_active.boolean = True
    is_active.short_description = "Active"


admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory)
admin.site.register(Tag)
admin.site.register(Product, ProductAdmin)
