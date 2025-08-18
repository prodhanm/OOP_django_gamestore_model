from django import forms
from .models import InventoryTransaction, StockSetting
from store.models import Product

class StockAdjustmentForm(forms.ModelForm):
    """Form for manual stock adjustments"""
    
    class Meta:
        model = InventoryTransaction
        fields = ['product', 'transaction_type', 'quantity', 'reason', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter choices for manual adjustments
        self.fields['transaction_type'].choices = [
            ('IN', 'Stock In'),
            ('OUT', 'Stock Out'),
            ('ADJUSTMENT', 'Manual Adjustment'),
            ('RETURN', 'Return'),
        ]
        
        self.fields['reason'].choices = [
            ('PURCHASE', 'Purchase from Supplier'),
            ('DAMAGED', 'Damaged Goods'),
            ('EXPIRED', 'Expired Products'),
            ('MANUAL', 'Manual Adjustment'),
            ('RETURN', 'Customer Return'),
            ('INITIAL', 'Initial Stock'),
            ('CORRECTION', 'Stock Correction'),
        ]

class BulkStockAdjustmentForm(forms.Form):
    """Form for bulk stock adjustments via CSV upload"""
    csv_file = forms.FileField(
        help_text="Upload a CSV file with columns: product_slug, quantity, transaction_type, reason, notes",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    
class QuickStockForm(forms.Form):
    """Quick form for adding/removing stock from product detail page"""
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        label="Quantity", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'})
    )
    action = forms.ChoiceField(
        choices=[('add', 'Add Stock'), ('remove', 'Remove Stock')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reason = forms.ChoiceField(
        choices=InventoryTransaction.TRANSACTION_REASONS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes'})
    )

class StockSettingsForm(forms.ModelForm):
    """Form for managing global stock settings"""
    
    class Meta:
        model = StockSetting
        fields = ['low_stock_threshold', 'allow_negative_stock', 'auto_adjust_on_sale']
        widgets = {
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_negative_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_adjust_on_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StockFilterForm(forms.Form):
    """Form for filtering inventory transactions"""
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        empty_label="All Products",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types')] + InventoryTransaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reason = forms.ChoiceField(
        choices=[('', 'All Reasons')] + InventoryTransaction.TRANSACTION_REASONS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )