from .models import InventoryAlert
from .utils import get_inventory_summary

def inventory_context(request):
    """
    Context processor to add inventory information to templates
    """
    if request.user.is_authenticated and request.user.is_staff:
        active_alerts_count = InventoryAlert.objects.filter(is_active=True).count()
        inventory_summary = get_inventory_summary()
        
        return {
            'inventory_alerts_count': active_alerts_count,
            'inventory_summary': inventory_summary,
        }
    
    return {}