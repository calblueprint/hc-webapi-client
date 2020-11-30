from modules.authentication.authentication import Authentication
import requests


class APIRequests:
    def __init__(self):
        self.auth = None

    def post(self, end_point, data={}):
        self.update_token()

        url = self.auth.get_base_url() + end_point
        return requests.post(url, data, headers=self.headers)

    def update_token(self):
        if self.auth is None:
            self.auth = Authentication()

        if not self.auth.is_valid_token():
            self.auth.update_token()

        self.headers = {
            'Authorization': self.auth.get_token()
        }
