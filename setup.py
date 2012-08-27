#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


import os

here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here,  'README.rst'))
long_description = f.read().strip()
f.close()


setup(
    name='tivix-django-braintree',
    version='0.1.1',
    author='Sumit Chachra',
    author_email='chachra@tivix.com',
    url='http://github.com/tivix/django-braintree',
    description = 'An easy way to integrate with Braintree Payment Solutions from Django.',
    long_description=long_description,
    keywords = 'django braintree payment',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.2.3',
        'South>=0.7.2',
        'braintree>=2.10.0',
        'django-common>=0.1',
        'fudge==1.0.3'
    ],
    #dependency_links=["git://github.com/Tivix/django-common.git@91e23cd5e0e8b420e8d4#egg=django_common-0.1"],
    test_suite = 'django_braintree.tests',
    include_package_data=True,
    # cmdclass={},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
