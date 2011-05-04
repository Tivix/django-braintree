from django.db import models
from django.contrib.auth.models import User


class UserVaultManager(models.Manager):
    def get_user_vault_instance_or_none(self, user):
        """Returns a vault_id string or None"""
        qset = self.filter(user=user)
        if not qset:
            return None
        
        if qset.count() > 1:
            raise Exception('This app does not currently support multiple vault ids')
        
        return qset.get().vault_id
    
    def is_in_vault(self, user):
        return True if self.filter(user=user) else False
    
    def charge(self, user, vault_id=None):
        """If vault_id is not passed this will assume that there is only one instane of user and vault_id in the db."""
        assert self.is_in_vault(user)
        if vault_id:
            user_vault = self.get(user=user, vault_id=vault_id)
        else:
            user_vault = self.get(user=user)

class UserVault(models.Model):
    """Keeping it open that one user can have multiple vault credentials, hence the FK to User and not a OneToOne."""
    user = models.ForeignKey(User, unique=True)
    vault_id = models.CharField(max_length=64, unique=True)
    
    objects = UserVaultManager()
    
    def __unicode__(self):
        return user

class PaymentLog(models.Model):
    """
    Captures raw charges made to a users credit card. Extra info related to this payment should be a OneToOneField
    referencing this model.
    """
    user = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=128)
    
    def __unicode__(self):
        return '%s charged $%s - %s' % (self.user, self.amount, self.transaction_id)
