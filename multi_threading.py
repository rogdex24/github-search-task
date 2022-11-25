import requests
import pandas as pd
import config
from email_scrape import get_email
import threading
from queue import Queue
from timeit import default_timer as timer

start = timer()

queue = Queue()

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


def get_user_info(idx, user_url):
    """ Populates the user information """

    # Get data of all users
    user_info_params = ["name", "login",
                        "bio", "location", "email", "html_url"]
    start_user = timer()

    data = []
    resp = requests.get(user_url, headers=headers)
    user = resp.json()

    for param in user_info_params:
        if param == "bio" and user["bio"] is not None:
            data.append(user[param].strip())
        elif param == "email" and user["email"] is None:
            email = get_email(user["html_url"])
            data.append(email)
        else:
            data.append(user[param])

    print("->", timer() - start_user, end="s\n")
    user_info[idx]= data


def fill_queue_and_list(user_list):
    # Get API url of all users
    user_urls = []
    for idx, user in enumerate(user_list):
        user_urls.append(user["url"])
        queue.put( [idx, user["url"]] )


def worker():
    while not queue.empty():
        user = queue.get()
        get_user_info(user[0], user[1])

""" main """

query = create_query(query_params)

user_list = get_user_list(query, headers)
user_count = len(user_list)
print(f"Found {user_count} users")

user_urls = fill_queue_and_list(user_list)

user_info = [[]]*user_count

thread_list = []

# Creating n/2 threads
for t in range(5):
    thread = threading.Thread(target=worker)
    thread_list.append(thread)

for thread in thread_list:
    thread.start()

for thread in thread_list:
    thread.join()

# user_info = get_user_info(user_list)


# Parsing into csv
user_df = pd.DataFrame(user_info, columns=[
                       "Name", "Github Handle", "Bio", "Location", "Email", "Github Link"])

user_df.to_csv('user_info_multi.csv', index=False)

print("Saved the results to user_info.csv")

end = timer()
print("multi-threaded:", end - start, "s")

# order won't be the same

# time: 4.307239899993874
