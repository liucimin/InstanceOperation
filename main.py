from Token import *
from Instance import *
from Neutron import *
import logging

logger = logging.getLogger('OpenstackController')  # 获取名为tst的logger


def main():
    setup_logging()
    url = r'http://'
    t = Token(url, 'admin', 'ADMIN_PASS', 'admin')
    token = t.get_token()
    im = InstanceManger(url, token)
    nm = NeutronManger(url, token)
    #clear the resources
    #im.clear_instance()
    #nm.clear_ports()
    #create instances
    #im.create_instances(63, nm)
    #im.create_instances_by_fixips('','',10,nm)

    #im.create_instances_by_created_port('','', nm, az = 'compute1')


def setup_logging():
    """Sets up the logging options for a log with supplied name."""
    import logging.handlers

    LOG_FILE = 'OpenstackController.log'

    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
    fmt = '[%(asctime)s][%(filename)s:%(lineno)s][%(name)s][%(levelname)s]%(message)s'

    formatter = logging.Formatter(fmt)  # 实例化formatter
    handler.setFormatter(formatter)  # 为handler添加formatter
    logger.addHandler(handler)  # 为logger添加handler
    logger.setLevel(logging.DEBUG)


if __name__ == "__main__":

    main()