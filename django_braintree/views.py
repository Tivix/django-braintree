import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

from braintree import Customer
from django_common.http import JsonResponse
from django_common.helper import form_errors_serialize
from django_common.decorators import ssl_required

from django_braintree.forms import UserCCDetailsForm
from django_braintree.models import UserVault


BAD_CC_ERROR_MSG = 'Oops! Doesn\'t seem like your Credit Card details are correct. Please re-check and try again.'

@ssl_required()
@login_required
def payments_billing(request, template='django_braintree/payments_billing.html'):
    """
    Renders both the past payments that have occurred on the users credit card, but also their CC information on file
    (if any)
    """
    d = {}
    
    if request.method == 'POST':
        # Credit Card is being changed/updated by the user
        form = UserCCDetailsForm(request.user, True, request.POST)
        if form.is_valid():
            response = form.save()
            if response.is_success:
                messages.add_message(request, messages.SUCCESS, 'Your credit card information has been securely saved.')
                return JsonResponse()
            else:
                return JsonResponse(success=False, errors=[BAD_CC_ERROR_MSG])
        
        return JsonResponse(success=False, data={'form': form_errors_serialize(form)})
    else:
        if UserVault.objects.is_in_vault(request.user):
            try:
                response = Customer.find(UserVault.objects.get_user_vault_instance_or_none(request.user).vault_id)
                d['current_cc_info'] = response.credit_cards[0]
            except Exception, e:
                logging.error('Unable to get vault information for user from braintree. %s' % e)
        d['cc_form'] = UserCCDetailsForm(request.user)
    
    return render(request, template, d)
