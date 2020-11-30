from modules.apirequests.apirequests import APIRequests


class Company:

    INVALID_REQUEST = 4
    STATUS_OK = 5

    def get_reports(self, auth, start_date, end_date):

        data = {
            'start_date': start_date,
            'end_date': end_date
        }

        end_point = "api/foodSafetyReports/"

        result = APIRequests().post(end_point, data)

        # if the request is successful, returns the access and refresh tokens
        if result.status_code == 200:
            obj = result.json()

            return Company.STATUS_OK, obj
        else:
            obj = result.json()
            print(obj['error'])
            return Company.INVALID_REQUEST, None

        # if something goes wrong, returns None
