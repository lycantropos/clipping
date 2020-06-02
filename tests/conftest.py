import os
import platform

from hypothesis import (HealthCheck,
                        settings)

on_azure_pipelines = bool(os.getenv('TF_BUILD', False))
on_travis_ci = bool(os.getenv('CI', False))
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=((settings.default.max_examples
                                         // (2 * (1 + is_pypy)))
                                        if on_azure_pipelines or on_travis_ci
                                        else settings.default.max_examples),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])
