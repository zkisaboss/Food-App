import json
import os
import random


"""
The program is designed to create a food recommendation system based on user preferences, clicks, and impressions.
The user can create an account or log in to an existing one.
A list of food options is provided to the user, and they must choose their preferences through a series of binary comparisons.
The program then creates a list of tuples containing the food options chosen by the user.
The preferences are then analyzed, and a dictionary of clicks, impressions, and click-through rates (CPI) is generated.
The user's account is updated with this data, which is stored in a JSON file.
The ToolBox class provides helpful functionality to be used throughout the program, such as a similarity score and a method to proceed or retry.
"""


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


class DataCollector:
    """
    Takes integers: '1' and '2'.
    Returns dictionaries: clicks, impressions.
    """

    def __init__(self):
        self.clicks = {}
        self.impressions = {}
        self.options = [
            "pizza", "chicken", "rice", "noodles", "tandoori chicken",
            "spaghetti", "sushi", "steak", "hamburger", "tacos",
            "barbecue ribs", "dumplings", "soup", "waffles", "pulled pork",
            "grilled salmon", "calamari",
        ]
        self.collect_preferences()

    @staticmethod
    def arrange(a, b):
        print(f"Do you prefer: {a} or {b}?")
        return (a, b) if int(input("Enter 1 for the first option or 2 for the second: ")) == 1 else (b, a)

    def store(self, a, b):
        self.clicks[a] = self.clicks.get(a, 0) + 1
        self.impressions[a] = self.impressions.get(a, 0) + 1
        self.impressions[b] = self.impressions.get(b, 0) + 1

    def collect_preferences(self):
        a = random.choice(self.options)
        for _ in range(5):
            b = random.choice([x for x in self.options if x != a])
            a, b = self.arrange(a, b)
            self.store(a, b)
            self.options.remove(b)

        self.options.remove(a)

    def __iter__(self):
        return iter((self.clicks, self.impressions))


class DataManager:
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
    def calculate_cpi(d1, d2):
        d3 = {}
        for key in d1:
            d3[key] = d1[key] / d2[key] * 100
        return dict(sorted(d3.items(), key=lambda item: item[1], reverse=True))

    def update(self, user):
        user["clicks"] = self.clicks
        user["impressions"] = self.impressions
        user["cpi"] = self.calculate_cpi(self.clicks, self.impressions)

        with open(user_file, "w") as f:
            json.dump(user, f, indent=4, separators=(',', ': '))


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


"""
Additional Resources:
https://towardsdatascience.com/introduction-to-recommender-systems-6c66cf15ada

https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ReuY4yOoqKMatHNJupcM5A@2x.png
https://miro.medium.com/v2/resize:fit:1400/format:webp/1*J7bZ-K-6RwmwlYUqoXFOOQ@2x.png

- Avoid a "rich-get-richer" effect for popular items 
- Avoid getting users stuck into an "information confinement area."
One solution is a hybrid-based approach, e.g., user-user and item-item collaborative filtering.

Todo (user-user):
1. Identify users with the most similar "interactions profile" (nearest neighbors or 'NN').
    i) Iterate through the NN's profile and append items not found in the current user profile to a list (new suggestions)
    ii) Iterate through the following NN's profile and append items not found in the current user profile to the list (new suggestions).
    iii) Repeat step ii until the list (new suggestions) contains five or more items.

2. Suggest items that are the most popular among these neighbors (and new to our user).
3. Brainstorm ways to avoid availability bias.
"""


class NNearestNeighbors:
    def __init__(self, n=5):
        self.user_file = user_file
        self.directory = 'Profiles/'
        self.n = n

    @staticmethod
    def compare(d1, d2):
        shared_keys = d1.keys() & d2.keys()
        num_keys = len(shared_keys)

        if num_keys == 0:
            return 0.00

        total_similarity = sum(abs(d1[key] - d2[key]) for key in shared_keys)
        return round(total_similarity / num_keys, 2)

    @property
    def get(self):
        data = []

        for file in os.listdir(self.directory):
            if self.user_file == f"Profiles/{file}":
                continue

            with open(os.path.join(self.directory, file), 'r') as f:
                loaded_user = json.load(f)

                if loaded_user["cpi"]:
                    difference = self.compare(user["cpi"], loaded_user["cpi"])
                    username = next(iter(loaded_user))
                    data.append((difference, username, loaded_user["cpi"]))

        data = sorted(data, key=lambda x: x[0])[:self.n]
        for element in data:
            print(f"{element} \n")


if __name__ == '__main__':
    USER = AccountManager().manage

    user_file = f"Profiles/{USER}.json"
    with open(user_file, "r") as f:
        user = json.load(f)

    NNearestNeighbors(3).get

    while True:
        clicks, impressions = DataCollector()
        DataManager(clicks, impressions)

        if ToolBox().proceed():
            break
