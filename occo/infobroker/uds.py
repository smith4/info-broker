#
# Copyright (C) 2014 MTA SZTAKI
#
# User Data Store for the OCCO InfoBroker
#

__all__ = ['UDS']

import occo.util.factory as factory
import occo.infobroker as ib
from occo.infobroker.kvstore import KeyValueStore
import logging

log = logging.getLogger('occo.infobroker.uds')

@ib.provider
class UDS(ib.InfoProvider, factory.MultiBackend):
    def __init__(self, info_broker, **backend_config):
        self.kvstore = KeyValueStore(**backend_config)
        self.ib = info_broker

    def infra_key(self, infra_id, dynamic):
        return 'infra:{0!s}{1!s}'.format(infra_id,
                                         ':state' if dynamic else '')
    def get_infra(self, infra_id, dynamic):
        return self.kvstore.query_item(self.infra_key(infra_id, dynamic))

    def auth_data_key(self, backend_id, user_id):
        return 'auth:{0!s}:{1!s}'.format(backend_id, user_id)
    def target_key(self, backend_id):
        return 'backend:{0!s}'.format(backend_id)

    def node_def_key(self, node_type):
        return 'node_def:{0!s}'.format(node_type)
    @ib.provides('node.definition.all')
    def all_nodedef(self, node_type):
        return self.kvstore.query_item(self.node_def_key(node_type))
    @ib.provides('node.definition')
    def nodedef(self, node_type, preselected_backend_id=None):
        return self.get_one_definition(node_type, preselected_backend_id)

    @ib.provides('backends.auth_data')
    def auth_data(self, backend_id, user_id):
        return self.kvstore.query_item(
            self.auth_data_key(backend_id, user_id))
    @ib.provides('backends')
    def target(self, backend_id):
        return self.kvstore.query_item(
            self.target_key(backend_id))

    @ib.provides('infrastructure.name')
    def infra_name(self, infra_id, **kwargs):
        return self.get_infra(infra_id, False).name

    @ib.provides('infrastructure.static_description')
    def infra_descr(self, infra_id, **kwargs):
        return self.get_infra(infra_id, False)

    @ib.provides('node.state')
    def get_node_state(self, node_id):
        return 'running?'

    @ib.provides('infrastructure.dynamic_state')
    def infra_state(self, infra_id, **kwargs):
        try:
            retval = self.get_infra(infra_id, True)
            if not retval:
                return dict()
        except KeyError:
            return dict()
        else:
            for node in retval.itervalues():
                for instance in node.itervalues():
                    instance['state'] = self.ib.get('node.state',
                                                    instance['node_id'])
            return retval

    def get_one_definition(self, node_type, preselected_backend_id):
        all_definitions = self.all_nodedef(node_type)
        if preselected_backend_id:
            return next(i for i in all_definitions
                        if i['backend_id'] == preselected_backend_id)
        else:
            import random
            return random.choice(all_definitions)
    def add_infrastructure(self, static_description):
        raise NotImplementedError()
    def remove_infrastructure(self, infra_id):
        raise NotImplementedError()
    def register_started_node(self, infra_id, node_id, instance_data):
        raise NotImplementedError()
    def remove_node(self, infra_id, node_name, instance_id):
        raise NotImplementedError()

@factory.register(UDS, 'dict')
class DictUDS(UDS):
    def add_infrastructure(self, static_description):
        self.kvstore.set_item(self.infra_key(static_description.infra_id, False),
                              static_description)
    def remove_infrastructure(self, infra_id):
        pass
    def register_started_node(self, infra_id, node_name, instance_data):
        node_id = instance_data['node_id']
        infra_key = self.infra_key(infra_id, True)
        infra_state = self.infra_state(infra_id)
        node_list = infra_state.setdefault(node_name, dict())
        node_list[node_id] = instance_data
        self.kvstore.set_item(infra_key, infra_state)
    def remove_node(self, infra_id, node_name, instance_id):
        pass

@factory.register(UDS, 'redis')
class DictUDS(UDS):
    def get_one_definition(self, node_type, preselected_backend_id):
        # TODO implement exploiting redis features
        pass

    def add_infrastructure(self, static_description):
        self.kvstore.set_item(self.infra_key(static_description.infra_id, False),
                              static_description)
    def remove_infrastructure(self, infra_id):
        pass
    def register_started_node(self, infra_id, node_name, instance_data):
        node_id = instance_data['node_id']
        infra_key = self.infra_key(infra_id, True)
        infra_state = self.infra_state(infra_id)
        node_list = infra_state.setdefault(node_name, dict())
        node_list[node_id] = instance_data
        self.kvstore.set_item(infra_key, infra_state)
    def remove_node(self, infra_id, node_name, instance_id):
        pass