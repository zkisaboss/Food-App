import json
import os
import random

# Implement TensorFlow recommendations instead of static methods.
nearby_foods = ["sushi", "grilled salmon", "steak", "tacos", "hamburger", "waffles", "noodles", "barbecue ribs",
                "pizza", "calamari", "pulled pork", "chicken", "dumplings", "rice", "tandoori chicken", "soup",
                "burritos"]


class AccountManager:
    @staticmethod
    def signup() -> str:
        for _ in range(3):
            USER = input("Enter a username: ")
            if os.path.exists(f"Profiles/{USER}.json"):
                print("Error: Username already exists.")
            else:
                break
        else:
            print("Raising SystemExit")
            raise SystemExit

        PASS = input("Enter a password: ")

        with open(f"Profiles/{USER}.json", "w") as fn:
            init = {food: 0 for food in nearby_foods}
            account = {USER: PASS, "clicks": init, "impressions": init, "cpi": init}
            json.dump(account, fn, indent=4, separators=(',', ': '))

        print("Account created successfully!")
        return USER

    @staticmethod
    def login() -> str:
        for _ in range(3):
            USER = input("Enter your username: ")
            PASS = input("Enter your password: ")

            try:
                with open(f"Profiles/{USER}.json", "r") as fn:
                    account = json.load(fn)

                unseen = set(nearby_foods) - set(account['impressions'])
                for i in unseen:
                    account['clicks'][i] = 0
                    account['impressions'][i] = 0
                    account['cpi'][i] = 0

                with open(f"Profiles/{USER}.json", "w") as fn:
                    json.dump(account, fn, indent=4, separators=(',', ': '))

                if account[USER] == PASS:
                    return USER
            except (FileNotFoundError, KeyError):
                print("Could not load profile.")

            print("Invalid username/password combination.")

        print("You've exceeded the number of login attempts.")
        raise SystemExit

    def interaction(self) -> str:
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
    def manage(self) -> str:
        return self.interaction()


class DataCollector:
    def __init__(self):
        self.clicks = {}
        self.impressions = {}
        self.recommendations = recommendations
        self.collect_data()

    @staticmethod
    def arrange(a: str, b: str) -> tuple:
        print(f"Do you prefer: {a} or {b}?")
        return (a, b) if int(input("Enter 1 for the first option or 2 for the second: ")) == 1 else (b, a)

    def store(self, a: str, b: str):
        self.clicks[a] = self.clicks.get(a, 0) + 1
        self.impressions[a] = self.impressions.get(a, 0) + 1
        self.impressions[b] = self.impressions.get(b, 0) + 1

    def collect_data(self):
        a = self.recommendations[0]

        for i in range(5):
            b = self.recommendations[i + 1]
            a, b = self.arrange(a, b)
            self.store(a, b)

    def __iter__(self):
        return iter((self.clicks, self.impressions))


class DataHandler:
    def __init__(self, c: dict, i: dict):
        self.clicks = self.merge(c, user["clicks"])
        self.impressions = self.merge(i, user["impressions"])
        self.update(user)

    @staticmethod
    def merge(d1: dict, d2: dict) -> dict:
        for k, v in d1.items():
            d2[k] = d2.get(k, 0) + v

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def modify_cpi(d1: dict, d2: dict) -> dict:
        d3 = {}
        for k in d1:
            try:
                d3[k] = d1[k] / d2[k] * 100
            except (KeyError, ZeroDivisionError):
                d3[k] = 0

        return dict(sorted(d3.items(), key=lambda item: item[1], reverse=True))

    def update(self, user):
        user["clicks"] = self.clicks
        user["impressions"] = self.impressions
        user["cpi"] = self.modify_cpi(self.clicks, self.impressions)

        with open(my_json, "w") as fn:
            json.dump(user, fn, indent=4, separators=(',', ': '))


class NearestNeighbors:
    def __init__(self):
        self.seen_files = set(f'{USER}.json')
        self.directory = os.listdir('Profiles/')
        self.num_neighbors = range(round(len(self.directory) ** 0.6666666666666666))

    @staticmethod
    def calculate_difference(d1: dict, d2: dict) -> float:
        shared_keys = d1.keys() & d2.keys()
        if not shared_keys:
            return 0.00

        key_difference_sum = sum(abs(d1[k] - d2[k]) for k in shared_keys)
        return key_difference_sum / len(shared_keys)

    def get_unseen_profile(self) -> tuple:
        unseen_files = set(self.directory) - self.seen_files
        random_file = random.choice(list(unseen_files))
        self.seen_files.add(random_file)

        with open(os.path.join('Profiles/', random_file), 'r') as file:
            json_data = dict(json.load(file)["cpi"])

        return random_file, json_data

    @property
    def get(self) -> list:
        data = []

        for _ in self.num_neighbors:
            username, json_data = self.get_unseen_profile()
            similarity = self.calculate_difference(user["cpi"], json_data)
            data.append((similarity, username, json_data))

        return sorted(data, key=lambda x: x[0])


class RecommendationHandler:
    def __init__(self):
        self.seen_items = set()
        self.nearest = self.merge(*[d[-1] for d in nearest[:3]])

    @staticmethod
    def merge(*dicts) -> dict:
        result = {}
        for d in dicts:
            for k, v in d.items():
                result[k] = result.get(k, []) + [v]
        return {k: sum(v) / len(v) for k, v in result.items()}

    @staticmethod
    def suggested_ele(dct: dict) -> str:
        unseen_keys = [k for k in dct if dct[k] == 0]
        probability = 0.1 if unseen_keys else 0.0

        total = sum(dct.values())
        weights = [(v / total) * 0.9 for v in dct.values() if v != 0]
        weights += [probability / len(unseen_keys) for _ in unseen_keys]

        return random.choices(list(dct.keys()), weights)[0]


    @property
    def get(self) -> list:
        recommendations = []

        while True:
            item = self.suggested_ele(self.nearest)
            if item in self.seen_items:
                continue

            self.seen_items.add(item)
            recommendations.append(item)

            if len(recommendations) == 6:
                break

        return sorted(recommendations, key=lambda x: self.nearest[x], reverse=True)


def proceed() -> int:
    print("Do you want to proceed or retry?")
    return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 1


if __name__ == '__main__':
    USER = AccountManager().manage

    my_json = f"Profiles/{USER}.json"
    with open(my_json, "r") as f:
        user = json.load(f)

    while True:
        nearest = NearestNeighbors().get
        recommendations = RecommendationHandler().get
        clicks, impressions = DataCollector()
        DataHandler(clicks, impressions)

        if proceed():
            break

    print("Loading Search Results...")
