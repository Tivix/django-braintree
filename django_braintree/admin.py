from django.contrib import admin

from django_braintree.models import UserVault, PaymentLog


admin.site.register(UserVault)
admin.site.register(PaymentLog)
