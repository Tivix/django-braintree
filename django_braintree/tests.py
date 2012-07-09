import fudge
from django.test import TestCase
from django.contrib.auth.models import User
from models import UserVault, PaymentLog
from decimal import Decimal
from django.core.management import call_command
from django.db.models import loading

loading.cache.loaded = False
call_command('syncdb', interactive=False)


class FakeTransaction(object):
    def __init__(self):
        self.id = 1


class FakeResponse(object):
    def __init__(self):
        self.is_success = True
        self.transaction = FakeTransaction()


@fudge.patch('braintree.Transaction.sale')
def fake_charge(vault, amount, FakeTransactionSale):
    (FakeTransactionSale.expects_call()
              .with_args()
              .returns(FakeResponse())
              )
    vault.charge(Decimal(amount))


class PayTest(TestCase):

    def test_charge(self):

        # Create user vault data
        user = User.objects.create_user('test', 'test@tivix.com', 'test')
        vault = UserVault.objects.create(user=user, vault_id="1cf373103e6657b96421348a")

        # Try charge account using FUDGE
        fake_charge(vault, 10)

        # Check if PaymentLog is Saved
        self.failUnlessEqual(PaymentLog.objects.all().count(), 1)
