#
# Copyright (C) 2014 MTA SZTAKI
#
# Configuration primitives for the SZTAKI Cloud Orchestrator
#

"""
Example
-------
``provider.yaml``

.. code-block:: yaml

    --- !TestRouter
    sub_providers:
        - !TestProviderA
        - !TestProviderB

``inforouter_example.py``

.. code-block:: python

    import datetime
    import occo.infobroker as ib

    # For all @provider classes, a YAML constructor will be
    # defined and registered.
    #
    # In all @provider classes, @provides methods will be registered
    # as for the given key.
   
    @ib.provider
    class TestProviderA(ib.InfoProvider):

        @ib.provides("global.echo")
        def echo(self, msg, **kwargs):
            return msg

        @ib.provides("global.time")
        def gettime(self):
            return datetime.datetime.now()

    @ib.provider
    class TestProviderB(ib.InfoProvider):

        @ib.provides("global.hello")
        def hithere(self, **kwargs): # <-- ... this.
            return 'Hello World!'

    @ib.provider
    class TestRouter(ib.InfoRouter):
        pass

    # Providers and sub-providers will be automatically instantiated
    # using pre-defined YAML constructors.
    with open('config.yaml') as f
        provider = config.DefaultYAMLConfig(f)

    print provider.get("global.hello") # <- This will call ...
"""

from provider import *

class MainInfoBroker(object):
    """
    Proxy object for the main, singleton info broker.

    Storing a simple reference to the main info broker is insufficient. In this
    case, the order of processing and instantiating the configured architecture
    affects what objects see as the main info broker--most of the time
    :data:`None`.

    Using a proxy implements late binding: objects will see the real info broker
    whenever they try to use it.

    This implies, that objects cannot *use* the main info broker in their
    ``__init__`` method. They can cache it however (``self.ib = ...``), that's
    the point of using a proxy.
    """
    def __getattribute__(self, name):
        global real_main_info_broker
        return real_main_info_broker.__getattribute__(name)

real_main_info_broker = None
main_info_broker = MainInfoBroker()
