import importlib
import os

import pytest
import social_core.backends as backends
from social_core.backends.oauth import BaseOAuth2

package_path = backends.__path__[0]


@pytest.fixture
def backends():
    backend_instances = []
    for module in os.listdir(package_path):
        try:
            module_instance = importlib.import_module("social_core.backends.%s" % module[:-3])
            backend_instances.extend([
                attr for attr in module_instance.__dict__.values()
                if type(attr) is type and all([
                    issubclass(attr, BaseOAuth2),
                    attr is not BaseOAuth2,
                ])
            ])
        except ImportError:
            continue
    return backend_instances
