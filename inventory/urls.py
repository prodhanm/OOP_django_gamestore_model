from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    
    # Transactions
    path('transactions/', views.inventory_transactions, name='inventory_transactions'),
    
    # Stock adjustments
    path('adjust/', views.stock_adjustment, name='stock_adjustment'),
    path('quick-adjust/', views.quick_stock_adjustment, name='quick_stock_adjustment'),
    path('bulk-adjust/', views.bulk_stock_adjustment, name='bulk_stock_adjustment'),
    
    # Alerts
    path('alerts/', views.stock_alerts, name='stock_alerts'),
    path('alerts/resolve/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    
    # Settings
    path('settings/', views.stock_settings, name='stock_settings'),
    
    # Reports
    path('report/', views.stock_report, name='stock_report'),
]