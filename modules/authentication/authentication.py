import os.path
import requests
import datetime


class Authentication:

    # feedback when something goes wrong
    STATUS_FAILED_TO_LOAD_CREDENTIALS = 1
    STATUS_FAILED_TO_GET_TOKEN = 2
    STATUS_AUTHENTICATION_OK = 3

    _CREDENTIALS_FILE = ".hc_account"
    _TOKENS_FILE = ".hc_tokens"

    def __init__(self):
        self.baseUrl = None
        self.accessToken = None
        self.refreshToken = None

    def get_base_url(self):
        return self.baseUrl

    # this will get a new token from the web_api
    def authenticate(self):
        # Tries to get credentials from <CREDENTIALS_FILE>
        credentials = self.get_credentials()

        # If it wasn't able to get the credentials
        # Returns that information
        if credentials is None:
            return Authentication.STATUS_FAILED_TO_LOAD_CREDENTIALS

        # Tries to get the tokens from the web api
        accessToken, refreshToken = self._get_new_token(credentials)

        # If it fails
        # Returns that information
        if accessToken is None:
            return Authentication.STATUS_FAILED_TO_GET_TOKEN

        # Saves the received tokens
        self.accessToken = accessToken
        self.refreshToken = refreshToken

        # Saved when the token was received
        self.createdTime = datetime.datetime.now()

        # save data to file
        self.save_tokens()

        # At the end of the process, returns the successful flag
        return Authentication.STATUS_AUTHENTICATION_OK

    # Will do the request to get a new token with the provided credentials
    def _get_new_token(self, credentials):
        try:
            # Saves the base url for future requests
            self.baseUrl = "http://%s.heavyconnect.com/" % (credentials['company'])
            url = self.baseUrl + "auth/"
            # Does the request with username and password
            result = requests.post(url, data={
                'username': credentials['username'],
                'password': credentials['password']
            })
            # if the request is successful, returns the access and refresh tokens
            if result.status_code == 200:
                obj = result.json()
                return obj['accessToken'], obj['refreshToken']

            # if something goes wrong, returns None
            return None, None

        # If some unexpected thing happens, like missing internet and others
        # Returns None
        # This can also be changed to send a better feedback in order to
        # provide more information about the error
        except Exception:
            return None, None

    def update_token(self):
        if self.accessToken is None:
            tokens = self.get_tokens()

            if tokens is None:
                return self.authenticate()

            self.accessToken = tokens['accessToken']
            self.refreshToken = tokens['refreshToken']
            self.createdTime = tokens['createdTime']
            self.baseUrl = tokens['baseUrl']

        if self._is_valid_refresh_token():
            try:
                # Saves the base url for future requests
                url = self.baseUrl + "refresh/"

                # Does the request with username and password
                result = requests.post(url, data={
                    'accessToken': self.accessToken,
                    'refreshToken': self.refreshToken
                })

                # if the request is successful, returns the access and refresh tokens
                if result.status_code == 200:
                    obj = result.json()
                    self.accessToken = obj['accessToken']
                    self.refreshToken = obj['refreshToken']
                    self.createdTime = datetime.datetime.now()

                    self.save_tokens()

                    return Authentication.STATUS_AUTHENTICATION_OK

                # if something goes wrong, returns None
                return Authentication.STATUS_FAILED_TO_GET_TOKEN

            # If some unexpected thing happens, like missing internet and others
            # Returns None
            except Exception as e:
                print(e.message)
                return None

        # If the refreshToken is not valid, we have to authenticate with
        # username and password
        else:
            return self.authenticate()

    # Checks if the current refreshToken is valid
    def _is_valid_refresh_token(self):
        # If it was never set, it is invalid!
        if self.refreshToken is None:
            return False

        # Check if the time difference from when the token was created is
        # bigger than 24 hours (expiration date of a refreshToken)
        now = datetime.datetime.now()
        return self._get_time_difference_in_hours(self.createdTime, now) < 24

    # Checks if the current accessToken is valid
    def is_valid_token(self):
        # If it was never set, it is invalid!
        if self.accessToken is None:
            return False

        # Check if the time difference from when the token was created is
        # bigger than 1 hour (expiration date of an accessToken)
        now = datetime.datetime.now()
        return self._get_time_difference_in_hours(self.createdTime, now) < 1

    def _get_time_difference_in_hours(self, date_start, date_end):
        date_difference = date_end - date_start

        difference = float(date_difference.days) / 24 \
            + float(date_difference.seconds) / (60 * 60)

        return difference

    # Returns the accessToken
    def get_token(self):
        return self.accessToken

    # Here we will try to get the credentials the <CREDENTIALS_FILE>
    def get_credentials(self):
        if(os.path.isfile(Authentication._CREDENTIALS_FILE)):
            credentials_file = open(Authentication._CREDENTIALS_FILE, 'r')

            credentials_content = credentials_file.read()

            # Tries get an object from the content in the <CREDENTIALS_FILE>
            try:
                credentials = eval(credentials_content)
            # If something goes wrong, it means that the file is not in a valid
            # format
            except Exception:
                return None

            # Checks if the credentials is an object of type dict
            if type(credentials) is dict:

                # For last, checks if the object contains what the informations
                # that we need to start the authentication process
                info = ['company', 'username', 'password']

                # If any of the fields described in 'info' is not in the dict
                if [x for x in info if x not in credentials]:
                    return None

                # If nothing went wrong, it returns the credentials
                return credentials
            # If not, it will return None
            else:
                return None

        # If the <CREDENTIALS_FILE> is not a file or doesn't exist
        else:
            return None

    def get_tokens(self):
        if(os.path.isfile(Authentication._TOKENS_FILE)):
            tokens_file = open(Authentication._TOKENS_FILE, 'r')
            tokens_content = tokens_file.read()

            # Tries get an object from the content in the <_TOKENS_FILE>
            try:
                tokens = eval(tokens_content)
            # If something goes wrong, it means that the file is not in a valid
            # format
            except Exception:
                return None

            # Checks if the credentials is an object of type dict
            if type(tokens) is dict:

                # For last, checks if the object contains what the informations
                # that we need to start the authentication process
                info = ['accessToken', 'refreshToken', 'createdTime', 'baseUrl', 'company', 'username', 'password']

                # If any of the fields described in 'info' is not in the dict
                if [x for x in info if x not in tokens]:
                    return None

                credentials = self.get_credentials()

                # Checks if credentials keep the same
                if credentials['company'] == tokens['company'] and credentials['username'] == tokens['username'] and credentials['password'] == tokens['password']:
                    # If nothing went wrong, it returns the credentials
                    return tokens

                # If note, it will return None
                else:
                    return None

            # If not, it will return None
            else:
                return None

        # If the <_TOKENS_FILE> is not a file or doesn't exist
        else:
            return None

    def save_tokens(self):
        token_file = open(Authentication._TOKENS_FILE, 'w')
        credentials = self.get_credentials()

        tokens = {
            'accessToken': self.accessToken,
            'refreshToken': self.refreshToken,
            'createdTime': self.createdTime,
            'baseUrl': self.baseUrl,
            'company': credentials['company'],
            'username': credentials['username'],
            'password': credentials['password']
        }

        # TODO: check if this will convert the data
        token_file.write(str(tokens))

        token_file.close()
