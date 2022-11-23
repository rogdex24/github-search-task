import requests
import pandas as pd
import config
from email_scrape import get_email
from tqdm import tqdm
from timeit import default_timer as timer
from datetime import datetime


now = datetime.now()
timestamp = datetime.timestamp(now)

start = timer()

headers = {
    "authorization": f"Bearer {config.api_token}"
}

URL = "https://api.github.com/search/users?q={}"

query_params = {
    "keyword": "hackathon",
    "location": "India",
    "followers": ">20",
    "repos": ">2",
    "language": "Python",
}


def create_query(query_params):
    """ Constructs the query from given parameters """

    if not any(query_params.values()):
        print("Insufficient search parameters given")
        print("Please input atleast one parameter")
        exit()

    query = ""
    for key in query_params.keys():
        if query_params[key]:
            if key == "keyword":
                query += query_params[key]
            else:
                query += f"{key}:{query_params[key]}"
            query += "+"

    return query


def get_user_list(query):
    """ API request for searching the users with given parameters """

    response = requests.get(URL.format(query), headers=headers)
    if response.status_code != 200:
        print("{} Bad Request".format(response.status_code))
        exit()
    user_response = response.json()
    user_list = user_response["items"]
    user_count = user_response["total_count"]
    return user_list, user_count


def get_user_info(user_list):
    """ Populates the user information """

    user_info = []
    user_info_params = ["name", "login",
                        "bio", "location", "email", "html_url"]

    for user in tqdm(user_list):
        api_url = user["url"]
        data = []
        resp = requests.get(api_url, headers=headers)
        user = resp.json()

        for param in user_info_params:
            if param == "bio" and user["bio"] is not None:
                data.append(user[param].strip())
            elif param == "email" and user["email"] is None:
                email = get_email(user["html_url"])
                data.append(email)
            else:
                data.append(user[param])

        user_info.append(data)

    return user_info


def convert_to_csv(data):
    """ Writes the user data obtained to a csv file """

    user_df = pd.DataFrame(data, columns=[
        "Name", "Github Handle", "Bio", "Location", "Email", "Github Link"])

    if data:
        filename = f'user_info_{timestamp}.csv'
        user_df.to_csv(filename, index=False)
        print("Saved the results to {}".format(filename))


query = create_query(query_params)

user_list, user_count = get_user_list(query)

print(f"Found {user_count} users")

user_info = get_user_info(user_list)

convert_to_csv(user_info)

end = timer()
print(end - start, end="s")
