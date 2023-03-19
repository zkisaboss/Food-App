import json
import os
import random


"""
To-Do:
- Find and Comment Bugs
- Fix Bugs

Planned Qualities:
- Adjusts Suggestions Based on Current Session Preferences.
    - Items that are frequently purchased together.
    - Items that are categorically similar.
    - Items that you've picked in the past.

- Avoids Information Confinement Area by Periodically Introduce New Items.
- Adjusts for Changing Trends.
"""


# Final Version
class AccountManager:
    """
    Takes string inputs: username and password.
    Returns a variable containing the username: USER.
    """

    @staticmethod
    def signup():
        while True:
            USER = input("Enter a username: ")
            if os.path.exists(f"Profiles/{USER}.json"):
                print("Username already exists. Please try a different username.")
            else:
                break

        PASS = input("Enter a password: ")
        account = {USER: PASS, "clicks": {}, "impressions": {}, "cpi": {}}

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
            user_input = input(
                "Enter '1' to create a new account or '2' to login to an existing one: ")

            if user_input == '1':
                return self.signup()
            elif user_input == '2':
                return self.login()
            else:
                print("Invalid choice. Please enter '1' or '2'.")

    @property
    def manage(self):
        return self.interaction()


# Planned: Session-Based Recommendations
class DataCollector:
    """
    Takes integers: '1' and '2'.
    Returns dictionaries: clicks, impressions.
    """

    def __init__(self):
        self.clicks = {}
        self.impressions = {}
        self.list = recommendations
        self.collect_data()

    @staticmethod
    def arrange(a, b):
        print(f"Do you prefer: {a} or {b}?")
        return (a, b) if int(input("Enter 1 for the first option or 2 for the second: ")) == 1 else (b, a)

    def store(self, a, b):
        self.clicks[a] = self.clicks.get(a, 0) + 1
        self.impressions[a] = self.impressions.get(a, 0) + 1
        self.impressions[b] = self.impressions.get(b, 0) + 1

    def collect_data(self):
        a = self.list[0]
        for i in range(total_decisions):
            b = self.list[i + 1]
            a, b = self.arrange(a, b)
            self.store(a, b)

    def __iter__(self):
        return iter((self.clicks, self.impressions))


# Final Version
class DataHandler:
    """
    Takes dictionaries: clicks, impressions.
    Updates the user's JSON file.
    """

    def __init__(self, c, i):
        self.clicks = self.merge(c, user["clicks"])
        self.impressions = self.merge(i, user["impressions"])
        self.update(user)

    @staticmethod
    def merge(d1, d2):
        for key, value in d1.items():
            d2[key] = d2.get(key, 0) + value

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def update_cpi(d1, d2):
        d3 = {}
        for key in d1:
            d3[key] = d1[key] / d2[key] * 100
        return dict(sorted(d3.items(), key=lambda item: item[1], reverse=True))

    def update(self, user):
        user["clicks"] = self.clicks
        user["impressions"] = self.impressions
        user["cpi"] = self.update_cpi(self.clicks, self.impressions)

        with open(my_json, "w") as f:
            json.dump(user, f, indent=4, separators=(',', ': '))


# Final Version
class NearestNeighbors:
    """
    Takes Current User's File: f'{USER}.file'
    Returns a list, which contains tuples: data
    """

    def __init__(self):
        self.seen_files = {f'{USER}.json'}
        self.directory = os.listdir('Profiles/')
        self.k_val = range(round(len(self.directory) ** (2 / 3)))

    @staticmethod
    def calculate_difference(d1, d2):
        shared_keys = d1.keys() & d2.keys()
        if not shared_keys:
            return 0.00

        key_difference_sum = sum(abs(d1[key] - d2[key]) for key in shared_keys)
        return round(key_difference_sum / len(shared_keys), 2)

    def get_unseen_profile(self):
        while True:
            _file = random.choice(self.directory)
            if _file not in self.seen_files:
                self.seen_files.add(_file)
                break

        with open(os.path.join('Profiles/', _file), 'r') as f:
            dct = dict(json.load(f)["cpi"])
        return _file, dct

    def get_nonempty_profile(self):
        while not (profile := self.get_unseen_profile())[1]:
            continue
        return profile

    @property
    def get(self):
        data = []

        for _ in self.k_val:
            username, json_data = self.get_nonempty_profile()
            similarity = self.calculate_difference(user["cpi"], json_data)
            data.append((similarity, username, json_data))

        return sorted(data, key=lambda x: x[0])


# Planned: Periodically Introduce New/Unique Items.
class RecommendationHandler:
    """
    Takes list of tuples: nearest
    Returns list of strings: recommendations
    """

    def __init__(self):
        self.seen_recommendations = set()
        self.elements = total_decisions + 1
        self.nearest = self.merge(nearest[0][-1], user["cpi"])

    @staticmethod
    def merge(d1, d2):
        for key, value in d1.items():
            d2[key] = d2.get(key, 0) + value

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def suggested_item(dct):
        return random.choice([k for k in dct for _ in range(int(dct[k]))])

    @property
    def get(self):
        recommendations = []

        while True:
            item = self.suggested_item(self.nearest)
            if item in self.seen_recommendations:
                continue

            self.seen_recommendations.add(item)
            recommendations.append(item)

            if len(recommendations) == self.elements:
                break

        return sorted(recommendations, key=lambda x: self.nearest[x], reverse=True)


# GOOD
class ToolBox:
    """
    Provides useful functionality to be used throughout the program.
    """

    @staticmethod
    def proceed():
        print("Do you want to proceed or retry?")
        return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 1

    @staticmethod
    def similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return round(score * 100, 2)

    @staticmethod
    def number_to_percent(d):
        return {
            key: d[key] / sum(d.values()) * 100
            for key in d
        }

    @staticmethod
    def filter_dict_list(list):
        return [i for i in list if isinstance(i, dict)]


if __name__ == '__main__':
    USER = AccountManager().manage

    my_json = f"Profiles/{USER}.json"
    with open(my_json, "r") as f:
        user = json.load(f)

    total_decisions = 5

    while True:
        nearest = NearestNeighbors().get
        recommendations = RecommendationHandler().get
        clicks, impressions = DataCollector()
        DataHandler(clicks, impressions)

        if ToolBox().proceed():
            break


"""
Additional Resources:
https://towardsdatascience.com/introduction-to-recommender-systems-6c66cf15ada

https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ReuY4yOoqKMatHNJupcM5A@2x.png
https://miro.medium.com/v2/resize:fit:1400/format:webp/1*J7bZ-K-6RwmwlYUqoXFOOQ@2x.png

- Avoid a "rich-get-richer" effect for popular items 
- Avoid getting users stuck into an "information confinement area."
One solution is a hybrid-based approach, e.g., user-user and item-item collaborative filtering.
"""
