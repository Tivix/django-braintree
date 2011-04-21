================
django-braintree
================




Installation
------------

- Install django_braintree (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a directory in your codebase.

- Add ``django_braintree`` to your Django settings ``INSTALLED_APPS``::
	
	INSTALLED_APPS = [
        # ...
        "django_braintree",
    ]

- If you're using South for schema migrations run ``python manage.py migrate django_braintree`` or simply do a ``syncdb``.


This opensource app is brought to you by Tivix, Inc. ( http://tivix.com/ )
