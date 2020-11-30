from modules.company.company import Company
from modules.authentication.authentication import Authentication

auth = Authentication()
c = Company()


"""
    Before start using, make sure you have the file `.hc_account`
    with all the fields filled with your company informations
"""


# Start Date of the range of reports to be pullend
startDate = "2020-05-22"

# End Date of the range of reports to be pullend
endDate = "2020-11-30"


status, reports = c.get_reports(auth, startDate, endDate)

print(reports)
