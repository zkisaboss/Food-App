import json
import os
import random


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
        for _ in range(total_decisions):
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


class NNearestNeighbors:
    """
    Takes positive integers: n
    Returns a list, which contains tuples: (sim_%, 'username', {dict})
    """

    def __init__(self, n=False):
        self.my_file = user_file
        self.directory = 'Profiles/'
        self.n = n or self.k_val()

    @staticmethod
    def compare(d1, d2):
        shared_keys = d1.keys() & d2.keys()

        if not shared_keys:
            return 0.00

        similarity = sum(abs(d1[key] - d2[key]) for key in shared_keys)
        return round(similarity / len(shared_keys), 2)

    def k_val(self):
        return round(len(os.listdir(self.directory)) ** (2/3))

    @property
    def get(self):
        data = []
        files = os.listdir(self.directory)
        seen_files = set()

        if self.n > self.k_val() and self.n >= len(files):
            sample_size = self.k_val()
        else:
            sample_size = max(self.n, self.k_val())

        for _ in range(sample_size):
            json_file = random.choice(files)
            while json_file == f"{USER}.json" or json_file in seen_files:
                json_file = random.choice(files)

            with open(os.path.join(self.directory, json_file), 'r') as f:
                their_dict = json.load(f)["cpi"]
                if not their_dict:
                    continue

                seen_files.add(json_file)
                diff = self.compare(user["cpi"], their_dict)
                data.append((diff, json_file[:-5], their_dict))

        data = sorted(data, key=lambda x: x[0])

        return data[:self.n]


class RecommendationHandler:
    """
    Takes list of tuples: [(sim, 'user', {dict}), (sim, 'user', {dict})...]
    Returns list of strings: ['food1', 'food2', 'food3]
    """

    def __init__(self):
        self.dict_list = [item[-1] for item in NN_List]
        self.total_decisions = total_decisions

    @staticmethod
    def merge(d1, d2):
        for key, value in d1.items():
            d2[key] = d2.get(key, 0) + value

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def suggested_item(dct):
        return random.choice([k for k in dct for _ in range(int(dct[k]))])

    @property
    def handle(self):
        recommendations = []
        seen = set()

        for dict in self.dict_list:
            merged = self.merge(dict, user["cpi"])

        while len(recommendations) < self.total_decisions:
            item = self.suggested_item(merged)

            if item not in seen:
                seen.add(item)
                recommendations.append(item)

        print(recommendations[:self.total_decisions])


"""
Additional Resources:
https://towardsdatascience.com/introduction-to-recommender-systems-6c66cf15ada

https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ReuY4yOoqKMatHNJupcM5A@2x.png
https://miro.medium.com/v2/resize:fit:1400/format:webp/1*J7bZ-K-6RwmwlYUqoXFOOQ@2x.png

- Avoid a "rich-get-richer" effect for popular items 
- Avoid getting users stuck into an "information confinement area."
One solution is a hybrid-based approach, e.g., user-user and item-item collaborative filtering.
"""


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

    user_file = f"Profiles/{USER}.json"
    with open(user_file, "r") as f:
        user = json.load(f)

    NN_List = NNearestNeighbors().get
    total_decisions = 5

    RecommendationHandler().handle

    while True:
        clicks, impressions = DataCollector()
        DataManager(clicks, impressions)

        if ToolBox().proceed():
            break
