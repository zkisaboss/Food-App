import json
import os
import random


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
                   "cpi": {}, "clicks": {}, "impressions": {}}

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
    Returns dictionaries: clicks, impressions.
    """

    def __init__(self, pref_hist):
        self.pref_hist = pref_hist
        self.extract = self.extract_data()

    def extract_data(self):
        clicks = {}
        impressions = {}

        for key1, key2 in self.pref_hist:
            clicks[key1] = clicks.get(key1, 0) + 1

            for key in [key1, key2]:
                impressions[key] = impressions.get(key, 0) + 1

        return clicks, impressions


class DataManager:
    """
    Takes dictionaries: clicks, impressions.
    Updates the user's JSON file.
    """

    def __init__(self, clicks, impressions):
        self.clicks = self.merge_dicts(clicks, user["clicks"])
        self.impressions = self.merge_dicts(
            impressions, user["impressions"])
        self.save(user)

    def merge_dicts(self, d1, d2):
        for key, value in d1.items():
            d2[key] = d2.get(key, 0) + value

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    def get_cpi(self, d1, d2):
        cpi = {
            key: (d1[key] / d2[key]) * 100
            for key in d2
            if d1.get(key) and d2.get(key)
        }
        return dict(sorted(cpi.items(), key=lambda item: item[1], reverse=True))

    def save(self, user):
        user["clicks"] = self.clicks
        user["impressions"] = self.impressions
        user["cpi"] = self.get_cpi(
            user["clicks"], user["impressions"])

        with open(user_file, "w") as f:
            json.dump(user, f, indent=4, separators=(',', ': '))


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
        print(
            f"The similarity of {n1} and {n2} is {round(score * 100, 2)}% ({int(score * (n1 + n2))}/{n1 + n2}).")
        return round(score * 100, 2)

    @staticmethod
    def number_to_percent(d):
        return {
            key: d[key] / sum(d.values()) * 100
            for key in d
        }


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

The consumer's similarity search must be light enough to run on their device.

todo (user-user):
1. Identify users with the most similar "interactions profile" (nearest neighbors or 'NN').
    i) Iterate through the NN's profile and append items not found in the current user profile to a list (new suggestions)
    ii) Iterate through the next NN's profile and append items not found in the current user profile to the list (new suggestions).
    iii) Repeat step ii until the list (new suggestions) contains five or more items.

2. Suggest items that are the most popular among these neighbors (and new to our user). <-- How much variance do I apply to the suggested items?
3. Brainstorm ways to avoid availability bias.
"""


class NearestNeighbors:
    def __init__(self):
        self.query = USER
        self.user_file = user_file
        self.directory = 'Profiles/'

    def calculate_similarity(self, n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return round(score * 100, 2)

    def compare_dicts(self, d1, d2):
        total_similarity = 0
        num_keys = len(d1)

        for key, val in d1.items():
            if key in d2:
                total_similarity += self.calculate_similarity(val, d2[key])
            else:
                num_keys -= 1

        return round(total_similarity / num_keys, 2) if num_keys > 0 else 0.00

    def run(self):
        data = []

        for file in os.listdir(self.directory):
            if self.user_file == f"Profiles/{file}":
                continue

            with open(os.path.join(self.directory, file), 'r') as f:
                loaded_user = json.load(f)

                if loaded_user["cpi"]:
                    similarity = self.compare_dicts(
                        user["cpi"], loaded_user["cpi"])
                    username = next(iter(loaded_user))

                    data.append(
                        (similarity, username, loaded_user["cpi"]))

        data = sorted(data, key=lambda x: x[0], reverse=True)
        print(data)
        return f"\nMy Dict: \n{USER}: {user['cpi']}\n \nMost Similar Dict ({data[0][0]}%): \n{data[0][1]}: {data[0][2]}\n"


if __name__ == '__main__':
    USER = AccountManager().manage

    user_file = f"Profiles/{USER}.json"
    with open(user_file, "r") as f:
        user = json.load(f)
    ####################
    nn = NearestNeighbors()
    result = nn.run()
    print(result)
    # Connect previous data to tuple collector
    pref_hist = TupleCollector().collect
    clicks, impressions = DataExtractor(pref_hist).extract
    DataManager(clicks, impressions)

    while retry := ToolBox().proceed_or_retry():
        pref_hist = TupleCollector().collect
        clicks, impressions = DataExtractor(pref_hist).extract
        DataManager(clicks, impressions)
