import json
import os
import random
import math


class AccountManager:
    """
    Takes string inputs: username and password.
    Returns a variable containing the username: USER.
    """

    def __init__(self):
        self.manage = self.interaction()

    @staticmethod
    def signup():  # Add a check to see if the username is already taken
        USER = input("Enter a username: ")
        PASS = input("Enter a password: ")
        account = {USER: PASS,
                   "global": {}, "global_pct": {}, "clicks": {}, "impressions": {}, "cpi": {}}

        with open(f"Profiles/{USER}.json", "w") as f:
            json.dump(account, f, indent=4, separators=(',', ': '))

        print("Account created successfully!")
        return USER

    @staticmethod
    def login():
        for _ in range(3):
            USER = input("Enter your username: ")
            PASS = input("Enter your password: ")

            try:
                with open(f"Profiles/{USER}.json", "r") as f:
                    account = json.load(f)

                if account[USER] == PASS:
                    return USER
            except (FileNotFoundError, KeyError):
                print("Could not load profile.")

            print("Invalid username/password combination.")

        print("You've exceeded the number of login attempts.")
        raise SystemExit

    def interaction(self):
        while True:
            choice = input(
                "Enter '1' to create a new account or '2' to login to an existing one: ")

            if choice == '1':
                return AccountManager.signup()
            elif choice == '2':
                return AccountManager.login()
            else:
                print("Invalid choice. Please enter '1' or '2'.")


class TupleCollector:
    """
    Takes integers: '1' and '2'.
    Returns a list, which contains tuples: pref_hist.
    """

    def __init__(self):
        self.options_list = [
            "pizza",
            "chicken",
            "rice",
            "noodles",
            "tandoori chicken",
            "spaghetti",
            "sushi",
            "steak",
            "hamburger",
            "tacos",
            "barbecue ribs",
            "dumplings",
            "soup",
            "waffles",
            "pulled pork",
            "grilled salmon",
            "calamari",
        ]
        self.collect = self.gather_pref()

    def preference(self, option1, option2):
        print(f"Do you prefer: {option1} or {option2}?")
        return int(input("Enter 1 for the first option or 2 for the second: "))

    def gather_pref(self):
        pref_hist = []
        opt1 = random.choice(self.options_list)

        for _ in range(min(4, len(self.options_list) - 1)):
            opt2 = random.choice(
                [option for option in self.options_list if option != opt1]
            )
            choice = self.preference(opt1, opt2)

            if choice == 2:
                opt1, opt2 = opt2, opt1

            pref_hist.append((opt1, opt2))
            self.options_list.remove(opt2)

        self.options_list.remove(opt1)
        return pref_hist


class DataExtractor:
    """
    Takes a list: pref_hist.
    Returns dictionaries: local, clicks, impressions.
    """

    def __init__(self, pref_hist):
        self.pref_hist = pref_hist
        self.extract = self.extract_data()

    def extract_data(self):
        local = {}
        clicks = {}
        impressions = {}

        for key1, key2 in self.pref_hist:

            if key1 not in local:
                local[key1] = local.get(key2, 0) + 1
            else:
                local[key1] += 1

            clicks[key1] = clicks.get(key1, 0) + 1

            for key in [key1, key2]:
                impressions[key] = impressions.get(key, 0) + 1

        return local, clicks, impressions


class DataManager:
    """
    Takes dictionaries: local, clicks, impressions.
    Updates the user's JSON file.
    """

    def __init__(self, local, clicks, impressions):
        self.global_dict = self.combine_dicts(local, account["global"])
        self.clicks = self.combine_dicts(clicks, account["clicks"])
        self.impressions = self.combine_dicts(
            impressions, account["impressions"])

        self.save_data(account)

    def combine_dicts(self, d1, d2):
        for key, value in d1.items():
            d2[key] = d2.get(key, 0) + value

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    def number_to_percent(self, d):
        return {
            key: d[key] / sum(d.values()) * 100
            for key in d
        }

    def get_cpi(self, d1, d2):
        cpi = {
            key: (d1[key] / d2[key]) * 100
            if d1.get(key) and d2.get(key)
            else 0.0
            for key in d2
        }
        return dict(sorted(cpi.items(), key=lambda item: item[1], reverse=True))

    def save_data(self, account):
        account["global"] = self.global_dict
        account["global_pct"] = self.number_to_percent(account["global"])

        account["clicks"] = self.clicks
        account["impressions"] = self.impressions
        account["cpi"] = self.get_cpi(
            account["clicks"], account["impressions"])

        with open(account_file, "w") as f:
            json.dump(account, f, indent=4, separators=(',', ': '))


class ToolBox:
    """
    Provides useful functionality to be used throughout the program.
    """

    @staticmethod
    def proceed_or_retry():
        print("Do you want to proceed or retry?")
        return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 2

    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} and {n2} is {round(score * 100, 2)}% ({int(score * (n1 + n2))}/{n1 + n2})."


"""
Additional Resources:
https://towardsdatascience.com/introduction-to-recommender-systems-6c66cf15ada

https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ReuY4yOoqKMatHNJupcM5A@2x.png
https://miro.medium.com/v2/resize:fit:1400/format:webp/1*J7bZ-K-6RwmwlYUqoXFOOQ@2x.png

It is necessary to be extremely careful to avoid a “rich-get-richer” effect for popular items
and to avoid getting users stuck into an “information confinement area”.
One solution is a hybrid-based approach, e.g. user-user and item-item collaborative filtering.

User-User: More Personalized, Less Robust. <-- BEST
Item-Item: More Robust, Less Personalized.

todo (user-user):
1. Identify users with the most similar “interactions profile” (nearest neighbors).
2. Suggest items that are the most popular among these neighbors (and new to our user).
"""


class NearestNeighbor:
    """
    Find users with the most similar interactions profile.
        - KNN (K-Nearest Neighbors): more accurate
        - ANN (Approximate Nearest Neighbor): more scalable
    """

    def cosine_similarity(self, a, b):
        """
        Calculates the cosine similarity between two dictionaries a and b.

        Args:
            a (dict): The first dictionary.
            b (dict): The second dictionary.

        Returns:
            float: The cosine similarity between the two dictionaries.
        """
        dot_product = 0
        norm_a = 0
        norm_b = 0

        for key in set(a.keys()) & set(b.keys()):
            dot_product += a[key] * b[key]
            norm_a += a[key] ** 2
            norm_b += b[key] ** 2

        if norm_a == 0 or norm_b == 0:
            return 0
        else:
            return dot_product / math.sqrt(norm_a * norm_b)

    def nearest_neighbor(self, q, data):
        """
        Finds the nearest neighbor of a query dictionary q in a list of dictionaries data.

        Args:
            q (dict): The query dictionary.
            data (list): The list of dictionaries to search.

        Returns:
            dict: The dictionary in data that is closest to q in terms of cosine similarity.
        """
        best_match = None
        best_similarity = 0

        for d in data:
            sim = self.cosine_similarity(q, d)

            if sim > best_similarity:
                best_match = d
                best_similarity = sim

        return best_match

    def run(self, user, directory):
        """
        Runs the nearest neighbor algorithm to find the closest user to a given query.

        Args:
            user (dict): The query dictionary.
            directory (str): The directory where user profiles are stored.

        Returns:
            dict: The dictionary in the directory that is closest to the query in terms of cosine similarity.
        """
        data = []
        for user_file in os.listdir(directory):
            if user_file != f"{user}.json":
                with open(os.path.join(directory, user_file), 'r') as f:
                    loaded_user = json.load(f)
                    data.append(loaded_user["cpi"])

        return self.nearest_neighbor(query, data)


if __name__ == '__main__':
    directory = 'Profiles/'
    query = {
        "steak": 88.88888888888889,
        "calamari": 75.0,
        "dumplings": 71.42857142857143,
        "waffles": 69.23076923076923,
        "barbecue ribs": 60.0,
        "hamburger": 55.55555555555556,
        "noodles": 50.0,
        "grilled salmon": 50.0,
        "pulled pork": 42.857142857142854,
        "rice": 37.5,
        "spaghetti": 33.33333333333333,
        "soup": 33.33333333333333,
        "chicken": 25.0,
        "tandoori chicken": 25.0,
        "tacos": 16.666666666666664,
        "sushi": 0.0,
        "pizza": 0.0
    }
    USER = AccountManager().manage

    nn = NearestNeighbor()
    result = nn.run(USER, directory)
    print(result)


    account_file = f"Profiles/{USER}.json"
    with open(account_file, "r") as f:
        account = json.load(f)

    pref_hist = TupleCollector().collect
    local, clicks, impressions = DataExtractor(pref_hist).extract

    DataManager(local, clicks, impressions)

    while retry := ToolBox().proceed_or_retry():
        pref_hist = TupleCollector().collect
        local, clicks, impressions = DataExtractor(pref_hist).extract

        DataManager(local, clicks, impressions)
