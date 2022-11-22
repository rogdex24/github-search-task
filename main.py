import requests
import pandas as pd
import config
from email_scrape import get_email
from timeit import default_timer as timer

start = timer()

headers = {
    "authorization": f"Bearer {config.api_token}"
}

url = "https://api.github.com/search/users?q={}"

query_params = {
    "keyword": "hackathon",
    "location": "India",
    "followers": ">1",
    "repos": ">2",
    "language": "Python",
}


def create_query(query_params):
    """ Constructs the query from given parameters """

    query = ""
    for key in query_params.keys():
        if query_params[key]:
            if key == "keyword":
                query += query_params[key]
            else:
                query += f"{key}:{query_params[key]}"
            query += "+"

    return query


def get_user_list(query, headers):
    """ API request for searching the users with given parameters """

    response = requests.get(url.format(query), headers=headers)
    user_response = response.json()
    user_list = user_response["items"]
    return user_list


def get_user_info(user_list):
    """ Populates the user information """
    # Get API url of all users
    user_urls = []
    for user in user_list:
        user_urls.append(user["url"])

    # Get data of all users
    user_info = []
    user_info_params = ["name", "login",
                        "bio", "location", "email", "html_url"]

    for api_url in user_urls:
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


query = create_query(query_params)

user_list = get_user_list(query, headers)
print(f"Found {len(user_list)} users")

user_info = get_user_info(user_list)


# Parsing into csv
user_df = pd.DataFrame(user_info, columns=[
                       "Name", "Github Handle", "Bio", "Location", "Email", "Github Link"])

user_df.to_csv('user_info.csv', index=False)

print("Saved the results to user_info.csv")

end = timer()
print(end - start, "s")