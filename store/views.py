from django.shortcuts import render
from . models import Category, Product
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

# Create your views here.
def store(request):
    all_products = Product.objects.prefetch_related('images').all()
    context = {'my_products': all_products}
    return render(request, 'store/store.html', context=context)

def categories(request):
    all_categories = Category.objects.all()
    return {'all_categories': all_categories}

def list_category(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category).prefetch_related('images')
    context = {'category': category, 'products': products}
    return render(request, 'store/list_category.html', context=context)

def product_info(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    product_images = product.images.all()
    context = {'product': product, 'product_images': product_images}
    return render(request, 'store/product_info.html', context=context)

def live_search(request):
    """
    Handle live search requests via AJAX
    Returns JSON response with matching products
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        
        if query:
            # Search in title, brand, and description
            products = Product.objects.filter(
                Q(title__icontains=query) | 
                Q(brand__icontains=query) | 
                Q(description__icontains=query),
                available=True  # Only show available products
            ).prefetch_related('images')[:20]  # Limit to 20 results for performance
            
            # Prepare data for JSON response
            results = []
            for product in products:
                main_image_url = ''
                if product.get_main_image():
                    main_image_url = product.get_main_image().url
                
                results.append({
                    'id': product.id,
                    'title': product.title,
                    'brand': product.brand,
                    'price': str(product.price),
                    'slug': product.slug,
                    'image_url': main_image_url,
                    'url': product.get_absolute_url()
                })
            
            return JsonResponse({
                'status': 'success',
                'results': results,
                'count': len(results)
            })
        else:
            return JsonResponse({
                'status': 'success',
                'results': [],
                'count': 0
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})