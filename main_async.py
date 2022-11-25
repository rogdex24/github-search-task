import requests
import aiohttp
import asyncio
import pandas as pd
import config
from email_scrape import get_email
from tqdm import tqdm
from timeit import default_timer as timer
from datetime import datetime


now = datetime.now()
timestamp = datetime.timestamp(now)

start_time = timer()

headers = {
    "authorization": f"Bearer {config.api_token}"
}

URL = "https://api.github.com/search/users?q={}"

query_params = {
    "keyword": "hackathon",
    "location": "India",
    "followers": ">1",
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


def convert_to_csv(data):
    """ Writes the user data obtained to a csv file """

    user_df = pd.DataFrame(data, columns=[
        "Name", "Github Handle", "Bio", "Location", "Email", "Github Link"])

    if data:
        filename = f'user_info_{timestamp}.csv'
        user_df.to_csv(filename, index=False)
        print("Saved the results to {}".format(filename))




async def get_user_info(session, user_url):
    """ Returns the user information """

    # Get data of all users
    user_info_params = ["name", "login",
                        "bio", "location", "email", "html_url"]
    
    async with session.get(user_url, headers=headers) as response:
        start_user = timer()
        user = await response.json()
        data = []

        for param in user_info_params:
            if param == "bio" and user["bio"] is not None:
                data.append(user[param].strip())
            elif param == "email" and user["email"] is None:
                email = get_email(user["html_url"])
                data.append(email)
            else:
                data.append(user[param])

        print(data[1])
        print("->", timer() - start_user, end="s")

        return data


async def main():

    async with aiohttp.ClientSession() as session:
        tasks = []

        for user in user_list:
            user_url = user['url']
            task = asyncio.ensure_future(get_user_info(session, user_url))
            tasks.append(task)


        user_info = await asyncio.gather(*tasks)

    print(len(user_info))

    # convert_to_csv(user_info)

query = create_query(query_params)

user_list, user_count = get_user_list(query)

print(f"Found {user_count} users")

asyncio.run(main())


print("-- %s s --" % (timer() - start_time))
