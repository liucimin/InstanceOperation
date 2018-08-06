import requests
import json
import time
import IPy
import logging

logger = logging.getLogger('OpenstackController')

class NeutronManger:
    def __init__(self, controllerAddress, token):

        self.__controllerAddress = controllerAddress
        self.__token = token


    def __get_port_by_uuid(self, uuid):

        pass

    def __get_ports(self):
        # X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        # /servers
        temp_url = "{}:9696/v2.0/{}".format(self.__controllerAddress, 'ports')
        r = requests.get(temp_url, headers=headers)
        try:
            return r.json()['ports']
        except Exception as e:
            logger.debug(e)

    def __get_all_ports_uuid(self):

        try:
            return [p['id'] for p in self.__get_ports()]
        except Exception as e:
            logger.debug(e)

    def delete_port(self, uuid=None):

        logger.debug('Deleting port: {}'.format(uuid))
        # /servers/
        # X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        # /servers
        temp_url = "{}:9696/v2.0/ports/{}".format(self.__controllerAddress, uuid)
        r = requests.delete(temp_url, headers=headers)
        if r.status_code != 204:
            raise Exception(str(r.status_code))
        time.sleep(1)

    def clear_ports(self):

        yes = input("Are u sure???")
        if yes == 'y':
            uuids = self.__get_all_ports_uuid()
            for uuid in uuids:
                try:
                    self.delete_port(uuid)
                except Exception as e:
                    logger.debug('Clear Ports Fail!!{}'.format(e))
                    return

    def create_ports(self, num = 0, type = 'normal', network_id = None):

        # X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        # /servers

        payload =     {"port": {
        "network_id": "{}".format(network_id),
        "binding:vnic_type":"{}".format(type)

    }}
        port_uuids = []
        ips = []
        for i in range(num):
            temp_url = "{}:9696/v2.0/ports".format(self.__controllerAddress)
            r = requests.post(temp_url, headers = headers, data=json.dumps(payload))
            if r.status_code == 201:
                port_uuids.append(r.json()["port"]['id'])
                ips.append( r.json()["port"]["fixed_ips"])

        return port_uuids,ips

    def create_port_by_fixedip(self, ip, type = 'normal', network_id = None):

        # X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        # /servers

        payload =     {"port": {
        "network_id": "{}".format(network_id),
        "binding:vnic_type":"{}".format(type),
        "fixed_ips": [{"ip_address":"{}".format(ip)}]

    }}
        port_uuids = []
        ips = []

        temp_url = "{}:9696/v2.0/ports".format(self.__controllerAddress)
        r = requests.post(temp_url, headers = headers, data=json.dumps(payload))
        if r.status_code == 201:
            port_uuids.append(r.json()["port"]['id'])
            ips.append( r.json()["port"]["fixed_ips"])

        return port_uuids,ips

    def make_ip_pool(self, startIp, endIp):

        tmpStartIp = IPy.IP(startIp)
        tmpEndIp = IPy.IP(endIp)

        return [str(IPy.IP(i)) for i in range(tmpStartIp.int() , tmpEndIp.int()  + 1)]


    def get_uuid_by_ip(self, ssip):

        ports = self.__get_ports()
        for p in ports:
            for fip in  p['fixed_ips']:
                if ssip == fip['ip_address']:
                    return p['id']
        return None



    # def clear_ports_by_fixip(self, startIp, endIp):
    #
    #     ippool = self.make_ip_pool(startIp, endIp)
    #     for ip in ippool:
    #
    #
    #         self.delete_port(uuid)

    #
    # def create_instances(self, num=0):
    #
    #     for i in num:
    #
    # def delete_special_instance(self, uuid=None, name=None):
    #
    #     if not uuid:
    #
    #         pass
    #     elif not name:
    #
    #         pass
    #     else:
    #
    #         # do log
    #         pass
    #
    #

