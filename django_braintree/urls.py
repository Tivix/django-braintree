from django.conf.urls import *


urlpatterns = patterns('django_braintree.views',
    url(r'^payments-billing/$', 'payments_billing', name='payments_billing'),
)
