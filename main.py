import json
import os
import random


"""
To-Do:
- Check for scalability

Planned Qualities:
- Adjusts Suggestions Based on Current Session Interactions.
    - Items that are frequently purchased together?
    - Items that are categorically similar?
    - Items that you've picked in the past?

- Avoids Information Confinement Area by Periodically Introduce New Items.
- Adjusts for Changing Trends.
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
        self.recommendations = recommendations
        self.collect_data()

    @staticmethod
    def arrange(a, b):
        print(f"Do you prefer: {a} or {b}?")
        return (a, b) if int(input("Enter 1 for the first option or 2 for the second: ")) == 1 else (b, a)

    def store(self, a, b):
        self.clicks[a] = self.clicks.get(a, 0) + 1
        self.impressions[a] = self.impressions.get(a, 0) + 1
        self.impressions[b] = self.impressions.get(b, 0) + 1

    # Planned: Session-Based Recommendations
    def collect_data(self):
        a = self.recommendations[0]
        
        for i in range(total_decisions):
            b = self.recommendations[i + 1]
            a, b = self.arrange(a, b)
            self.store(a, b)

    def __iter__(self):
        return iter((self.clicks, self.impressions))


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
        for k, v in d1.items():
            d2[k] = d2.get(k, 0) + v

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def modify_cpi(d1, d2):
        d3 = {k: d1[k] / d2[k] * 100 for k in d1}
        return dict(sorted(d3.items(), key=lambda item: item[1], reverse=True))

    def update(self, user):
        user["clicks"] = self.clicks
        user["impressions"] = self.impressions
        user["cpi"] = self.modify_cpi(self.clicks, self.impressions)

        with open(my_json, "w") as f:
            json.dump(user, f, indent=4, separators=(',', ': '))


class NearestNeighbors:
    """
    Takes Current User's File: f'{USER}.file'.
    Returns a list, which contains tuples: data.
    """

    def __init__(self):
        self.seen_files = {f'{USER}.json'}
        self.directory = os.listdir('Profiles/')
        self.num_neighbors = range(round(len(self.directory) ** (2 / 3)))

    @staticmethod
    def calculate_difference(d1, d2):
        shared_keys = d1.keys() & d2.keys()
        if not shared_keys:
            return 0.00

        key_difference_sum = sum(abs(d1[k] - d2[k]) for k in shared_keys)
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

        for _ in self.num_neighbors:
            username, json_data = self.get_nonempty_profile()
            similarity = self.calculate_difference(user["cpi"], json_data)
            data.append((similarity, username, json_data))

        return sorted(data, key=lambda x: x[0])


# Planned: Periodically Introduce New/Unique Items.
class RecommendationHandler:
    """
    Takes list of tuples: nearest.
    Returns list of strings: recommendations.
    """

    def __init__(self):
        self.seen_items = set()
        self.elements = total_decisions + 1
        self.nearest = self.merge(*[d[-1] for d in nearest[:3]])

    @staticmethod
    def merge(*dicts):
        result = {}
        for d in dicts:
            for k, v in d.items():
                result[k] = result.get(k, []) + [v]
        return {k: sum(v)/len(v) for k, v in result.items()}

    @staticmethod
    def suggested_ele(dct):
        return random.choice([k for k in dct for _ in range(int(dct[k]))])

    @property
    def get(self):
        recommendations = []

        while True:
            item = self.suggested_ele(self.nearest)
            if item in self.seen_items:
                continue

            self.seen_items.add(item)
            recommendations.append(item)

            if len(recommendations) == self.elements:
                break

        return sorted(recommendations, key=lambda x: self.nearest[x], reverse=True)


def proceed():
    print("Do you want to proceed or retry?")
    return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 1


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

        if proceed():
            break

    print("Loading Search Results...")
