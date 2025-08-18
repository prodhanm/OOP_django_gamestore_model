from django.contrib import admin
from . models import Product, Category, ProductImage
from django.utils.html import format_html

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display
    min_num = 0  # Minimum number of forms
    max_num = 10  # Maximum number of images per product
    fields = ['image', 'alt_text', 'is_main', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'slug', 'price', 'stock', 
                    'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    inlines = [ProductImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = "Images"
    
    def main_image_preview(self, obj):
        main_image = obj.get_main_image()
        if main_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                main_image.url
            )
        return "No image"
    main_image_preview.short_description = "Main Image"

