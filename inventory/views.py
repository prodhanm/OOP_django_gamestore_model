from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import csv
import json

from .models import InventoryTransaction, InventoryAlert, StockSetting
from .forms import StockAdjustmentForm, BulkStockAdjustmentForm, QuickStockForm, StockSettingsForm, StockFilterForm
from store.models import Product
from .utils import adjust_stock, create_inventory_alert, get_stock_settings

def is_staff(user):
    """Check if user is staff"""
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def inventory_dashboard(request):
    """Main inventory dashboard"""
    # Get summary statistics
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    out_of_stock_products = Product.objects.filter(stock=0).count()
    active_alerts = InventoryAlert.objects.filter(is_active=True).count()
    
    # Recent transactions
    recent_transactions = InventoryTransaction.objects.select_related('product', 'user')[:10]
    
    # Active alerts
    alerts = InventoryAlert.objects.filter(is_active=True).select_related('product')[:10]
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'active_alerts': active_alerts,
        'recent_transactions': recent_transactions,
        'alerts': alerts,
    }
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
@user_passes_test(is_staff)
def inventory_transactions(request):
    """List all inventory transactions with filtering"""
    form = StockFilterForm(request.GET or None)
    transactions = InventoryTransaction.objects.select_related('product', 'user').order_by('-created_at')
    
    if form.is_valid():
        if form.cleaned_data.get('product'):
            transactions = transactions.filter(product=form.cleaned_data['product'])
        if form.cleaned_data.get('transaction_type'):
            transactions = transactions.filter(transaction_type=form.cleaned_data['transaction_type'])
        if form.cleaned_data.get('reason'):
            transactions = transactions.filter(reason=form.cleaned_data['reason'])
        if form.cleaned_data.get('date_from'):
            transactions = transactions.filter(created_at__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            transactions = transactions.filter(created_at__date__lte=form.cleaned_data['date_to'])
    
    paginator = Paginator(transactions, 25)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    context = {
        'transactions': transactions,
        'form': form,
    }
    
    return render(request, 'inventory/transactions.html', context)

@login_required
@user_passes_test(is_staff)
def stock_adjustment(request):
    """Manual stock adjustment"""
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            transaction_type = form.cleaned_data['transaction_type']
            reason = form.cleaned_data['reason']
            notes = form.cleaned_data['notes']
            
            try:
                # Adjust stock using utility function
                adjust_stock(
                    product=product,
                    quantity=quantity,
                    transaction_type=transaction_type,
                    reason=reason,
                    notes=notes,
                    user=request.user
                )
                messages.success(request, f'Stock adjusted successfully for {product.title}')
                return redirect('inventory_dashboard')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = StockAdjustmentForm()
    
    context = {'form': form}
    return render(request, 'inventory/stock_adjustment.html', context)

@login_required
@user_passes_test(is_staff)
@require_POST
def quick_stock_adjustment(request):
    """AJAX endpoint for quick stock adjustments"""
    form = QuickStockForm(request.POST)
    if form.is_valid():
        product_id = form.cleaned_data['product_id']
        quantity = form.cleaned_data['quantity']
        action = form.cleaned_data['action']
        reason = form.cleaned_data['reason']
        notes = form.cleaned_data['notes']
        
        product = get_object_or_404(Product, id=product_id)
        
        # Determine transaction type based on action
        if action == 'add':
            transaction_type = 'IN'
        else:
            transaction_type = 'OUT'
            quantity = -abs(quantity)  # Ensure negative for stock removal
        
        try:
            adjust_stock(
                product=product,
                quantity=quantity,
                transaction_type=transaction_type,
                reason=reason,
                notes=notes,
                user=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Stock adjusted successfully for {product.title}',
                'new_stock': product.stock
            })
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid form data'
    })

@login_required
@user_passes_test(is_staff)
def bulk_stock_adjustment(request):
    """Bulk stock adjustment via CSV upload"""
    if request.method == 'POST':
        form = BulkStockAdjustmentForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            try:
                # Process CSV file
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(decoded_file)
                
                successful_updates = 0
                errors = []
                
                with transaction.atomic():
                    for row_num, row in enumerate(csv_reader, start=2):
                        try:
                            product = Product.objects.get(slug=row['product_slug'])
                            quantity = int(row['quantity'])
                            transaction_type = row['transaction_type'].upper()
                            reason = row['reason'].upper()
                            notes = row.get('notes', '')
                            
                            adjust_stock(
                                product=product,
                                quantity=quantity,
                                transaction_type=transaction_type,
                                reason=reason,
                                notes=notes,
                                user=request.user
                            )
                            successful_updates += 1
                            
                        except Product.DoesNotExist:
                            errors.append(f'Row {row_num}: Product with slug "{row["product_slug"]}" not found')
                        except ValueError as e:
                            errors.append(f'Row {row_num}: {str(e)}')
                        except Exception as e:
                            errors.append(f'Row {row_num}: Unexpected error - {str(e)}')
                
                if successful_updates > 0:
                    messages.success(request, f'Successfully updated {successful_updates} products')
                
                if errors:
                    for error in errors:
                        messages.error(request, error)
                
                return redirect('inventory_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = BulkStockAdjustmentForm()
    
    context = {'form': form}
    return render(request, 'inventory/bulk_adjustment.html', context)

@login_required
@user_passes_test(is_staff)
def stock_alerts(request):
    """View and manage stock alerts"""
    alerts = InventoryAlert.objects.select_related('product').order_by('-created_at')
    
    # Filter options
    active_only = request.GET.get('active_only', 'true') == 'true'
    if active_only:
        alerts = alerts.filter(is_active=True)
    
    alert_type = request.GET.get('alert_type')
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    alerts = paginator.get_page(page_number)
    
    context = {
        'alerts': alerts,
        'alert_types': InventoryAlert.ALERT_TYPES,
        'active_only': active_only,
        'selected_alert_type': alert_type,
    }
    
    return render(request, 'inventory/alerts.html', context)

@login_required
@user_passes_test(is_staff)
@require_POST
def resolve_alert(request, alert_id):
    """Resolve a stock alert"""
    alert = get_object_or_404(InventoryAlert, id=alert_id)
    alert.is_active = False
    alert.resolved_at = timezone.now()
    alert.resolved_by = request.user
    alert.save()
    
    return JsonResponse({'success': True})

@login_required
@user_passes_test(is_staff)
def stock_settings(request):
    """Manage global stock settings"""
    try:
        settings_obj = StockSetting.objects.get()
    except StockSetting.DoesNotExist:
        settings_obj = StockSetting.objects.create()
    
    if request.method == 'POST':
        form = StockSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock settings updated successfully')
            return redirect('stock_settings')
    else:
        form = StockSettingsForm(instance=settings_obj)
    
    context = {'form': form}
    return render(request, 'inventory/settings.html', context)

@login_required
@user_passes_test(is_staff)
def stock_report(request):
    """Generate stock level reports"""
    products = Product.objects.select_related('category').order_by('title')
    
    # Get filter parameters
    category = request.GET.get('category')
    stock_status = request.GET.get('stock_status')
    
    if category:
        products = products.filter(category__slug=category)
    
    if stock_status == 'low':
        settings = get_stock_settings()
        products = products.filter(stock__lt=settings.low_stock_threshold)
    elif stock_status == 'out':
        products = products.filter(stock=0)
    elif stock_status == 'negative':
        products = products.filter(stock__lt=0)
    
    # Export to CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product', 'Category', 'Current Stock', 'Price', 'Status'])
        
        for product in products:
            if product.stock == 0:
                status = 'Out of Stock'
            elif product.stock < 0:
                status = 'Negative Stock'
            elif product.stock < 10:  # You might want to make this configurable
                status = 'Low Stock'
            else:
                status = 'In Stock'
                
            writer.writerow([
                product.title,
                product.category.name if product.category else 'No Category',
                product.stock,
                product.price,
                status
            ])
        
        return response
    
    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': Product.objects.values_list('category__name', 'category__slug').distinct(),
    }
    
    return render(request, 'inventory/stock_report.html', context)
