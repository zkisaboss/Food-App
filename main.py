"""
todo:
- Add features.
"""

import json
import random


class AccountManager:
    """
    Functions in this class:
    Take username and password strings.
    Return username string.
    """

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
    Functions in this class:
    Take integers (1, 2).
    Return a list that contains tuples (pref_hist).
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
        self.pref_hist = self.gather_preferences()

    def preference(self, option1, option2):
        print(f"Do you prefer: {option1} or {option2}?")
        return int(input("Enter 1 for the first option or 2 for the second: "))

    def gather_preferences(self):
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
    Functions in this class:
    Take list (pref_hist).
    Return dictionaries (local, clicks, impressions).
    """

    def __init__(self, pref_hist):
        self.pref_hist = pref_hist

    def extract_data(self):
        local = {}
        clicks = {}
        impressions = {}
        for tuple in self.pref_hist:
            key1, key2 = tuple

            if key1 not in local:
                local[key1] = local.get(key2, 0) + 1
            else:
                local[key1] += 1

            clicks[key1] = clicks.get(key1, 0) + 1
            impressions |= {
                key: impressions.get(key, 0) + 1
                for key in [key1, key2]
            }

        return local, clicks, impressions


class DataManager:
    """
    Functions in this class:
    Take dictionaries.
    Write to the user's JSON file.
    """

    def __init__(self, local, clicks, impressions):
        self.global_dict = self.combine_dicts(local, profile["global"])
        self.clicks = self.combine_dicts(clicks, profile["clicks"])
        self.impressions = self.combine_dicts(
            impressions, profile["impressions"])

        self.save_profile_data(profile)

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

    def save_profile_data(self, profile):
        profile["global"] = self.global_dict
        profile["global_pct"] = self.number_to_percent(profile["global"])

        profile["clicks"] = self.clicks
        profile["impressions"] = self.impressions
        profile["cpi"] = self.get_cpi(
            profile["clicks"], profile["impressions"])

        with open(profile_file, "w") as f:
            json.dump(profile, f, indent=4, separators=(',', ': '))


class ToolBox:
    """
    The functions in this class:
    Provide useful functionality to be used throughout the program.
    """

    @staticmethod
    def proceed_or_retry():
        print("Do you want to proceed or retry?")
        return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 2

    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} and {n2} is {round(score * 100, 2)}% ({int(score * (n1 + n2))}/{n1 + n2})."


if __name__ == '__main__':
    username = AccountManager().interaction()

    profile_file = f"Profiles/{username}.json"
    with open(profile_file, "r") as f:
        profile = json.load(f)

    pref_hist = TupleCollector().pref_hist
    local, clicks, impressions = DataExtractor(
        pref_hist).extract_data()

    DataManager(local, clicks, impressions)

    while retry := ToolBox().proceed_or_retry():
        pref_hist = TupleCollector().pref_hist
        local, clicks, impressions = DataExtractor(
            pref_hist).extract_data()
        DataManager(local, clicks, impressions)
