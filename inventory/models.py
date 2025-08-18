from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.core.exceptions import ValidationError

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Manual Adjustment'),
        ('SALE', 'Sale'),
        ('RETURN', 'Return'),
    ]
    
    TRANSACTION_REASONS = [
        ('PURCHASE', 'Purchase from Supplier'),
        ('SALE', 'Product Sale'),
        ('DAMAGED', 'Damaged Goods'),
        ('EXPIRED', 'Expired Products'),
        ('MANUAL', 'Manual Adjustment'),
        ('RETURN', 'Customer Return'),
        ('INITIAL', 'Initial Stock'),
        ('CORRECTION', 'Stock Correction'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=TRANSACTION_REASONS)
    notes = models.TextField(blank=True, help_text="Additional notes about this transaction")
    
    # Stock levels before and after transaction
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    
    # User who made the transaction
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Related order item if transaction is from a sale
    order_item = models.ForeignKey('payment.OrderItem', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - {self.get_transaction_type_display()} - {self.quantity}"

    def clean(self):
        if self.transaction_type in ['OUT', 'SALE'] and self.quantity > 0:
            self.quantity = -abs(self.quantity)  # Ensure negative for outgoing
        elif self.transaction_type in ['IN', 'RETURN'] and self.quantity < 0:
            self.quantity = abs(self.quantity)  # Ensure positive for incoming

class InventoryAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock Warning'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('NEGATIVE_STOCK', 'Negative Stock Error'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    threshold = models.IntegerField(default=0, help_text="Stock level that triggered this alert")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Inventory Alert'
        verbose_name_plural = 'Inventory Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - {self.get_alert_type_display()}"

class StockSetting(models.Model):
    """Global settings for inventory management"""
    low_stock_threshold = models.IntegerField(default=10, help_text="Global low stock warning threshold")
    allow_negative_stock = models.BooleanField(default=False, help_text="Allow products to go into negative stock")
    auto_adjust_on_sale = models.BooleanField(default=True, help_text="Automatically adjust stock when orders are completed")
    
    class Meta:
        verbose_name = 'Stock Setting'
        verbose_name_plural = 'Stock Settings'

    def __str__(self):
        return "Stock Settings"

    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        if not self.pk and StockSetting.objects.exists():
            raise ValidationError('Only one StockSetting instance is allowed')
        return super().save(*args, **kwargs)