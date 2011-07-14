import logging
from datetime import datetime

from django import forms

from django_common.helper import md5_hash
from braintree import Customer, CreditCard
from django_braintree.models import UserVault


class UserCCDetailsForm(forms.Form):
    __MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    )

    __YEAR_CHOICES = (
        (2010, '2010'),
        (2011, '2011'),
        (2012, '2012'),
        (2013, '2013'),
        (2014, '2014'),
        (2015, '2015'),
        (2016, '2016'),
        (2017, '2017'),
        (2018, '2018'),
        (2019, '2019'),
        (2020, '2020'),
    )
    
    name = forms.CharField(max_length=64, label='Name as on card')
    
    cc_number = forms.CharField(max_length=16, label='Credit Card Number')
    expiration_month = forms.ChoiceField(choices=__MONTH_CHOICES)
    expiration_year = forms.ChoiceField(choices=__YEAR_CHOICES)
    
    zip_code = forms.CharField(max_length=8, label='Zip Code')
    cvv = forms.CharField(max_length=4, label='CVV')
    
    def __init__(self, user, post_to_update=False, *args, **kwargs):
        """
        Takes in a user to figure out whether a vault id exists or not etc.
        
        @post_to_update: if set to True, then form contents are meant to be posted to Braintree, otherwise its implied
        this form is meant for rendering to the user, hence initialize with braintree data (if any).
        """
        self.__user = user
        self.__user_vault = UserVault.objects.get_user_vault_instance_or_none(user)
        
        if not post_to_update and self.__user_vault and not args:
            logging.debug('Looking up payment info for vault_id: %s' % self.__user_vault.vault_id)
            
            try:
                response = Customer.find(self.__user_vault.vault_id)
                info = response.credit_cards[0]

                initial = {
                    'name': info.cardholder_name,
                    'cc_number': info.masked_number,
                    'expiration_month': int(info.expiration_month),
                    'expiration_year': info.expiration_year,
                    'zip_code': info.billing_address.postal_code,
                }
                super(UserCCDetailsForm, self).__init__(initial=initial, *args, **kwargs)
            except Exception, e:
                logging.error('Was not able to get customer from vault. %s' % e)
                super(UserCCDetailsForm, self).__init__(initial = {'name': '%s %s' % (user.first_name, user.last_name)},
                    *args, **kwargs)
        else:
            super(UserCCDetailsForm, self).__init__(initial = {'name': '%s %s' % (user.first_name, user.last_name)},
                *args, **kwargs)
    
    def clean(self):
        today = datetime.today()
        exp_month = int(self.cleaned_data['expiration_month'])
        exp_year = int(int(self.cleaned_data['expiration_year']))
        
        if exp_year < today.year or (exp_month <= today.month and exp_year <= today.year):
            raise forms.ValidationError('Please make sure your Credit Card expires in the future.')
        
        return self.cleaned_data
    
    def save(self, prepend_vault_id=''):
        """
        Adds or updates a users CC to the vault.
        
        @prepend_vault_id: any string to prepend all vault id's with in case the same braintree account is used by
        multiple projects/apps.
        """
        assert self.is_valid()
        
        cc_details_map = {    # cc details
            'number': self.cleaned_data['cc_number'],
            'cardholder_name': self.cleaned_data['name'],
            'expiration_date': '%s/%s' %\
                (self.cleaned_data['expiration_month'], self.cleaned_data['expiration_year']),
            'cvv': self.cleaned_data['cvv'],
            'billing_address': {
                'postal_code': self.cleaned_data['zip_code'],
            }
        }
        
        if self.__user_vault:
            try:
                # get customer info, its credit card and then update that credit card
                response = Customer.find(self.__user_vault.vault_id)
                cc_info = response.credit_cards[0]
                return CreditCard.update(cc_info.token, params=cc_details_map)
            except Exception, e:
                logging.error('Was not able to get customer from vault. %s' % e)
                self.__user_vault.delete()  # delete the stale instance from our db
        
        # in case the above updating fails or user was never in the vault
        new_customer_vault_id = '%s%s' % (prepend_vault_id, md5_hash()[:24])
        respone = Customer.create({    # creating a customer, but we really just want to store their CC details
            'id': new_customer_vault_id,   # vault id, uniquely identifies customer. We're not caring about tokens (used for storing multiple CC's per user)
            'credit_card': cc_details_map
        })
        
        if respone.is_success:  # save a new UserVault instance
            UserVault.objects.create(user=self.__user, vault_id=new_customer_vault_id)
        
        return respone
