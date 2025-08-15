from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import Order
from .utils import process_order_stock_adjustment

@receiver(post_save, sender=Order)
def handle_order_completion(sender, instance, created, **kwargs):
    """
    Handle stock adjustments when an order is created/completed
    This signal will automatically adjust inventory when orders are processed
    """
    if created:
        # Process stock adjustments for the new order
        try:
            process_order_stock_adjustment(instance)
        except Exception as e:
            # Log the error but don't prevent order creation
            print(f"Error processing stock adjustment for order {instance.id}: {e}")