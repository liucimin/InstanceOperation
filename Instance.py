import requests
import json
import time
import base64
import logging

logger = logging.getLogger('OpenstackController')

class InstanceManger:

    def __init__(self, controllerAddress, token):

        self.__controllerAddress = controllerAddress
        self.__token = token

    def __get_all_instances_uuid(self):

        #X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        #/servers
        temp_url = "{}:8774/v2.1/{}".format(self.__controllerAddress, 'servers')
        r = requests.get(temp_url, headers = headers)
        try:
            return [server['id'] for server in r.json()['servers']]

        except Exception as e:
            logger.error(e)
            return []

    def delete_instance(self, uuid = None):

        logger.debug('Deleting instance: {}'.format(uuid))
        # X-Auth-Token
        headers = {"X-Auth-Token": self.__token}
        temp_url = "{}:8774/v2.1/servers/{}".format(self.__controllerAddress, uuid)
        # /servers
        r = requests.delete(temp_url, headers = headers)
        if r.status_code != 204:
            raise Exception(str(r.status_code))
        time.sleep(3)

    def clear_instance(self):
        yes = input("Are u sure clear Instances ?    ")
        if yes == 'y':
            #Get all the instance uuid
            uuids = self.__get_all_instances_uuid()
            for uuid in uuids:
                try:
                    #loop to delete the instance from uuid
                    self.delete_instance(uuid)
                except Exception as e:
                    logger.error('Clear Instances Fail!!{}'.format(e))
                    return

    def create_instances(self, num = 0, nm = None, az = 'controller', networkid = ''):
        """
            Create nums instances.

        :param num:
        :param nm:
        :param az:
        :param networkid:
        :return: None
        """
        for i in range(num):

            #first create a port
            port_uuids, ips = nm.create_port( num = 1, type = 'direct', network_id = networkid)
            # make user_data
            user_data = self.make_user_data(ips)
            #make payload
            ip = ips[0][0]["ip_address"]

            #make the json payload
            payload = {"server": {"name": "sriov2_{}".format(ip.replace('.','-')), "imageRef": "e641a27f-9978-431f-a810-eb2544962dae",
                                  "config_drive" : True,"flavorRef": "2", "max_count": 1, "min_count": 1,
                                  "availability_zone": "nova:{}".format(az),"user_data":user_data,
                                  "networks": [{"port": "{}".format(port_uuids[0])}]}}
            headers = {"X-Auth-Token": self.__token,"Content-Type": "application/json"}
            #POST /servers
            temp_url = "{}:8774/v2.1/servers".format(self.__controllerAddress)
            r = requests.post(temp_url, headers=headers, data=json.dumps(payload))
            if r.status_code != 202:
                logger.error("Crashing!")
                logger.error(r)
                logger.error(i)
                return
            time.sleep(5)

        logger.debug('Succeed Create {} instances.'.format(i + 1))



    def create_instances_by_fixips(self,startIp, endIp, num = 0, nm = None, az = 'controller', networkid = ''):

        ippool = nm.make_ip_pool(startIp, endIp)
        for i in range(num):

            port_uuids, ips = nm.create_port_by_fixedip(ippool[i], type = 'direct', network_id = networkid)
            # make user_data
            user_data = self.make_user_data(ips)
            #make payload
            ip = ips[0][0]["ip_address"]
            payload = {"server": {"name": "sriov1_{}".format(ip.replace('.','-')), "imageRef": "e641a27f-9978-431f-a810-eb2544962dae",
                                  "config_drive" : True,"flavorRef": "2", "max_count": 1, "min_count": 1,
                                  "availability_zone": "nova:{}".format(az),"user_data":user_data,
                                  "networks": [{"port": "{}".format(port_uuids[0])}]}}
            headers = {"X-Auth-Token": self.__token,"Content-Type": "application/json"}
            #POST /servers
            temp_url = "{}:8774/v2.1/servers".format(self.__controllerAddress)
            r = requests.post(temp_url, headers=headers, data=json.dumps(payload))
            if r.status_code != 202:
                logger.error("Crashing!")
                logger.error(r)
                logger.error(i)
                return
            time.sleep(5)

        logger.debug('Succeed Create {} instances.'.format(i + 1))

    def create_instances_by_created_port(self,startIp, endIp, nm, az = 'controller'):

        ippool = nm.make_ip_pool(startIp, endIp)
        for i in range(len(ippool)):

            port_uuids = [nm.get_uuid_by_ip(ippool[i])]
            if port_uuids == [None]:
                logger.debug("Can't find the ip {}'s port!".format(ippool[i]))
                continue
            ips = [[{"ip_address":ippool[i]}]]
            # make user_data
            user_data = self.make_user_data(ips)
            #make payload
            ip = ips[0][0]["ip_address"]
            payload = {"server": {"name": "sriov2_{}".format(ip.replace('.','-')), "imageRef": "e641a27f-9978-431f-a810-eb2544962dae",
                                  "config_drive" : True,"flavorRef": "2", "max_count": 1, "min_count": 1,
                                  "availability_zone": "nova:{}".format(az),"user_data":user_data,
                                  "networks": [{"port": "{}".format(port_uuids[0])}]}}
            headers = {"X-Auth-Token": self.__token,"Content-Type": "application/json"}
            #POST /servers
            temp_url = "{}:8774/v2.1/servers".format(self.__controllerAddress)
            r = requests.post(temp_url, headers=headers, data=json.dumps(payload))
            if r.status_code != 202:
                logger.error("Crashing!")
                logger.error(r)
                logger.error(i)
                return
            time.sleep(5)

        logger.debug('Succeed Create {} instances.'.format(i + 1))


    def delete_special_instance(self, uuid = None, name = None):

        if not uuid:

            pass
        elif not name:

            pass
        else:

            #do log
            pass



    def make_user_data(self, ips):
        """
        Make the user data to generate a ifcfg-eth0 file.
        Use this to set the eth0 interface a ipadderss.
        :param ips:
        :return: Str
        """
        user_data = """#cloud-config
                   runcmd:
                   - echo DEVICE=eth0 > /etc/sysconfig/network-scripts/ifcfg-eth0
                   - echo BOOTPROTO=static >> /etc/sysconfig/network-scripts/ifcfg-eth0
                   - echo ONBOOT=yes >> /etc/sysconfig/network-scripts/ifcfg-eth0
                   - echo IPADDR={} >> /etc/sysconfig/network-scripts/ifcfg-eth0
                   - echo NETMASK=255.255.255.0 >> /etc/sysconfig/network-scripts/ifcfg-eth0
                   - echo GATEWAY=10.0.0.1 >> /etc/sysconfig/network-scripts/ifcfg-eth0
                   - [ cloud-init-per, once, restart_netconfig, service, network, restart ]""".format(
            ips[0][0]["ip_address"])
        logger.debug(user_data)
        #print(base64.b64encode(user_data.encode()))
        return base64.b64encode(user_data.encode()).decode()
