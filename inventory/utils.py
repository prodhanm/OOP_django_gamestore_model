from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, F
from .models import InventoryTransaction, InventoryAlert, StockSetting
from store.models import Product

def get_stock_settings():
    """Get or create stock settings"""
    settings, created = StockSetting.objects.get_or_create(
        defaults={
            'low_stock_threshold': 10,
            'allow_negative_stock': False,
            'auto_adjust_on_sale': True
        }
    )
    return settings

def adjust_stock(product, quantity, transaction_type, reason, notes="", user=None, order_item=None):
    """
    Adjust product stock and create inventory transaction record
    
    Args:
        product: Product instance
        quantity: Quantity to adjust (positive for additions, negative for reductions)
        transaction_type: Type of transaction (IN, OUT, ADJUSTMENT, SALE, RETURN)
        reason: Reason for the transaction
        notes: Optional notes
        user: User making the adjustment
        order_item: Related order item (for sales)
    
    Returns:
        InventoryTransaction instance
    
    Raises:
        ValueError: If adjustment would result in negative stock and it's not allowed
    """
    settings = get_stock_settings()
    
    with transaction.atomic():
        # Lock the product row to prevent race conditions
        product = Product.objects.select_for_update().get(pk=product.pk)
        
        previous_stock = product.stock
        new_stock = previous_stock + quantity
        
        # Check if negative stock is allowed
        if new_stock < 0 and not settings.allow_negative_stock:
            raise ValueError(f"Insufficient stock. Available: {previous_stock}, Requested: {abs(quantity)}")
        
        # Update product stock
        product.stock = new_stock
        product.save(update_fields=['stock'])
        
        # Create inventory transaction record
        inventory_transaction = InventoryTransaction.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=quantity,
            reason=reason,
            notes=notes,
            previous_stock=previous_stock,
            new_stock=new_stock,
            user=user,
            order_item=order_item
        )
        
        # Check for alerts
        create_inventory_alert(product, new_stock)
        
        return inventory_transaction

def create_inventory_alert(product, current_stock):
    """
    Create inventory alerts based on stock levels
    
    Args:
        product: Product instance
        current_stock: Current stock level
    """
    settings = get_stock_settings()
    
    # Clear existing active alerts for this product
    InventoryAlert.objects.filter(product=product, is_active=True).update(is_active=False)
    
    alert_type = None
    message = ""
    threshold = current_stock
    
    if current_stock < 0:
        alert_type = 'NEGATIVE_STOCK'
        message = f"{product.title} has negative stock ({current_stock})"
    elif current_stock == 0:
        alert_type = 'OUT_OF_STOCK'
        message = f"{product.title} is out of stock"
    elif current_stock < settings.low_stock_threshold:
        alert_type = 'LOW_STOCK'
        message = f"{product.title} is running low on stock ({current_stock} remaining)"
        threshold = settings.low_stock_threshold
    
    if alert_type:
        InventoryAlert.objects.create(
            product=product,
            alert_type=alert_type,
            message=message,
            threshold=threshold
        )

def process_order_stock_adjustment(order):
    """
    Process stock adjustments for a completed order
    
    Args:
        order: Order instance
    """
    settings = get_stock_settings()
    
    if not settings.auto_adjust_on_sale:
        return
    
    # Import here to avoid circular imports
    from payment.models import OrderItem
    
    order_items = OrderItem.objects.filter(order=order)
    
    for item in order_items:
        try:
            adjust_stock(
                product=item.product,
                quantity=-item.quantity,  # Negative because it's a sale
                transaction_type='SALE',
                reason='SALE',
                notes=f'Order #{order.id} - {item.product.title}',
                user=order.user,
                order_item=item
            )
        except ValueError as e:
            # Log the error but don't stop processing other items
            print(f"Error adjusting stock for {item.product.title}: {e}")
            continue

def bulk_stock_update(products_data, user=None):
    """
    Bulk update stock for multiple products
    
    Args:
        products_data: List of dictionaries with product and stock info
        user: User making the changes
    
    Returns:
        Dictionary with success and error counts
    """
    results = {'success': 0, 'errors': []}
    
    for data in products_data:
        try:
            product = Product.objects.get(pk=data['product_id'])
            adjust_stock(
                product=product,
                quantity=data['quantity'],
                transaction_type=data.get('transaction_type', 'ADJUSTMENT'),
                reason=data.get('reason', 'MANUAL'),
                notes=data.get('notes', ''),
                user=user
            )
            results['success'] += 1
        except Exception as e:
            results['errors'].append({
                'product_id': data.get('product_id'),
                'error': str(e)
            })
    
    return results

def get_stock_history(product, days=30):
    """
    Get stock history for a product
    
    Args:
        product: Product instance
        days: Number of days to look back
    
    Returns:
        QuerySet of InventoryTransaction instances
    """
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    return InventoryTransaction.objects.filter(
        product=product,
        created_at__gte=start_date
    ).order_by('-created_at')

def get_low_stock_products():
    """
    Get all products with low stock
    
    Returns:
        QuerySet of Product instances
    """
    settings = get_stock_settings()
    return Product.objects.filter(stock__lt=settings.low_stock_threshold)

def get_out_of_stock_products():
    """
    Get all products that are out of stock
    
    Returns:
        QuerySet of Product instances
    """
    return Product.objects.filter(stock=0)

def calculate_stock_value():
    """
    Calculate total value of current stock
    
    Returns:
        Decimal: Total stock value
    """
    from django.db.models import Sum, F
    from decimal import Decimal
    
    result = Product.objects.aggregate(
        total_value=Sum(F('stock') * F('price'))
    )
    return result['total_value'] or Decimal('0.00')

def get_inventory_summary():
    """
    Get inventory summary statistics
    
    Returns:
        Dictionary with inventory statistics
    """
    settings = get_stock_settings()
    
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
    total_value = calculate_stock_value()
    
    low_stock_count = Product.objects.filter(stock__lt=settings.low_stock_threshold).count()
    out_of_stock_count = Product.objects.filter(stock=0).count()
    negative_stock_count = Product.objects.filter(stock__lt=0).count()
    
    active_alerts = InventoryAlert.objects.filter(is_active=True).count()
    
    return {
        'total_products': total_products,
        'total_stock': total_stock,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'negative_stock_count': negative_stock_count,
        'active_alerts': active_alerts,
    }