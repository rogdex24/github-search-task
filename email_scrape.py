import requests
import re


def get_email(url):
    """ Extracts email from user's github profile readme """

    response = requests.get(url)

    EMAIL_REGEX = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    user_email = re.findall(EMAIL_REGEX, response.text, re.I)

    if len(user_email) == 0:
        return "NA"

    return user_email[0]




# Email Regex Validation Pattern from [https://emailregex.com/]
