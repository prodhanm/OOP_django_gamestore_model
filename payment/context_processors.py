from django.conf import settings

def paypal_settings(request):
    return {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    }