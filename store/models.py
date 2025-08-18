from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=250, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('list_category', args=[self.slug])
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, default='un-branded')
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=250)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    # Documenting the removal of the image field to create a product image model
    #image = models.ImageField(upload_to='images/')
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'products'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('product_info', args=[self.slug])

    def get_main_image(self):
        """Return the first image or None if no images exist"""
        first_image = self.images.first()
        return first_image.image if first_image else None
    
    def get_all_images(self):
        """Return all images for this product"""
        return self.images.all()
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    is_main = models.BooleanField(default=False, help_text="Check if this is the main product image")
    order = models.PositiveIntegerField(default=0, help_text="Order of image display")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Images'
        ordering = ['order', 'created']

    def __str__(self):
        return f"{self.product.title} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        """Ensure only one main image per product"""
        if self.is_main:
            # Set all other images for this product to not be main
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
