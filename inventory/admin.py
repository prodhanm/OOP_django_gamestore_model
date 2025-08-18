from django.contrib import admin
from .models import InventoryTransaction, InventoryAlert, StockSetting

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'reason', 'previous_stock', 'new_stock', 'user', 'created_at']
    list_filter = ['transaction_type', 'reason', 'created_at', 'product__category']
    search_fields = ['product__title', 'notes', 'user__username']
    readonly_fields = ['previous_stock', 'new_stock', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('product', 'transaction_type', 'quantity', 'reason')
        }),
        ('Stock Information', {
            'fields': ('previous_stock', 'new_stock')
        }),
        ('Additional Information', {
            'fields': ('notes', 'user', 'order_item', 'created_at')
        }),
    )

@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_type', 'threshold', 'is_active', 'created_at', 'resolved_by']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['product__title', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    list_per_page = 20
    
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_active=False,
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = "Mark selected alerts as resolved"

@admin.register(StockSetting)
class StockSettingAdmin(admin.ModelAdmin):
    list_display = ['low_stock_threshold', 'allow_negative_stock', 'auto_adjust_on_sale']
    
    def has_add_permission(self, request):
        # Only allow one settings record
        return not StockSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
