from functools import partial

import factory
from django.contrib.auth import get_user_model, models as auth_models

from .test_utils import factories_utils

class BaseUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    name = factory.Faker('first_name')
    phone = factory.Sequence(lambda n: '+96601300%03d' % n)


class DriverFactory(BaseUserFactory):
    is_driver = True


class ClientFactory(UserFactory):
    is_superuser = False
    is_driver = False


class DispatcherFactory(UserFactory):
    is_superuser = True


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Location

    name = factory.Sequence(lambda n: 'location-{}'.format(n))
