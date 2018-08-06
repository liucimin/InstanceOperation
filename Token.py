import requests
import json
import logging

logger = logging.getLogger('OpenstackController')
class Token:

    def __init__(self, controllerAddress, user, password, project_name):

        self.__controllerAddress = controllerAddress
        self.user = user
        self.password = password
        self.project_name = project_name
        self.__token = None

    def __get_token(self):

        payload = { "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "{}".format(self.user),
          "domain": { "id": "default" },
          "password":  "{}".format(self.password)
        }
      }
    },
    "scope": {
      "project": {
        "name": "{}".format(self.project_name),
        "domain": { "id": "default" }
      }
    }
  }
}
        # http://localhost:5000/v3/auth/tokens
        temp_url = "{}:5000/v3/auth/tokens".format(self.__controllerAddress)
        headers = {"Content-Type": "application/json"}
        r = requests.post(temp_url, headers = headers, data=json.dumps(payload))
        try:

            self.__token = r.headers['X-Subject-Token']
            return self.__token
        except Exception as e:
            logger.error(e)

    def get_token(self):

        if not self.__token:

            return self.__get_token()

        else:
            return self.__token
