import json
import os
import random

# Implement TensorFlow recommendations instead of static methods.
nearby_foods = ["sushi", "grilled salmon", "steak", "tacos", "hamburger", "waffles", "noodles",
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

        with open(f"Profiles/{USER}.json", "w") as file:
            init = {food: 0 for food in nearby_foods}
            account = {USER: PASS, "clicks": init, "impressions": init, "cpi": init}
            json.dump(account, file, indent=4, separators=(',', ': '))

        print("Account created successfully!")
        return USER

    @staticmethod
    def login() -> str:
        for _ in range(3):
            USER = input("Enter your username: ")
            PASS = input("Enter your password: ")

            try:
                with open(f"Profiles/{USER}.json") as file:
                    account = json.load(file)

                with open(f"Profiles/{USER}.json", "w") as file:
                    unseen = set(nearby_foods) - set(account['impressions'])
                    for i in unseen:
                        account['clicks'][i] = 0
                        account['impressions'][i] = 0
                        account['cpi'][i] = 0
                    json.dump(account, file, indent=4, separators=(',', ': '))

                if account[USER] == PASS:
                    return USER
                else:
                    print("Invalid username/password combination.")
            except (FileNotFoundError, KeyError):
                print("Could not load profile.")


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
    def __init__(self, r):
        self.clicks = {}
        self.impressions = {}
        self.recommendations = r
        self.collect_data()

    @staticmethod
    def arrange(a: str, b: str) -> tuple:
        print(f"Do you prefer: {a} or {b}?")
        return (a, b) if input("Enter 1 for the first option or 2 for the second: ") == "1" else (b, a)

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
        self.clicks = self.merge(c, user_data["clicks"])
        self.impressions = self.merge(i, user_data["impressions"])
        self.update()

    @staticmethod
    def merge(d1: dict, d2: dict) -> dict:
        for k, v in d1.items():
            d2[k] = d2.get(k, 0) + v

        return d2

    @staticmethod
    def modify_cpi(d1: dict, d2: dict) -> dict:
        d3 = {}
        for k in d1:
            try:
                d3[k] = d1[k] / d2[k] * 100
            except (KeyError, ZeroDivisionError):
                d3[k] = 0

        return d3

    def update(self):
        user_data["clicks"] = self.clicks
        user_data["impressions"] = self.impressions
        user_data["cpi"] = self.modify_cpi(self.clicks, self.impressions)

        with open(f"Profiles/{username}.json", "w") as file:
            json.dump(user_data, file, indent=4, separators=(',', ': '))


class NearestNeighbors:
    def __init__(self, name: str):
        self.directory = os.listdir('Profiles/')
        self.directory.remove(f'{name}.json')
        self.unseen_files = set(self.directory)
        self.k_neighbors = round(len(self.directory) ** 0.6666666666666666)

    @staticmethod
    def calculate_difference(d1: dict, d2: dict) -> float:
        shared_keys = d1.keys() & d2.keys()
        if not shared_keys:
            return 0.0

        key_difference_sum = sum(abs(d1[k] - d2[k]) for k in shared_keys)
        return key_difference_sum / len(shared_keys)

    def get_unseen_profile(self) -> dict:
        random_file = random.choice(list(self.unseen_files))
        self.unseen_files.remove(random_file)

        with open(f"Profiles/{random_file}") as file:
            json_data = json.load(file)["cpi"]

        return json_data

    @property
    def get(self) -> list:
        dicts = []
        scores = []
        for _ in range(self.k_neighbors):
            json_data = self.get_unseen_profile()
            dicts.append(json_data)

            similarity = self.calculate_difference(json_data, user_data["cpi"])
            scores.append(similarity)

        return sorted(dicts, key=lambda x: scores[dicts.index(x)])[:3]


class RecommendationHandler:
    def __init__(self, nearest_neighbors: list):
        self.seen = set()
        self.nearest = self.merge(*nearest_neighbors)
        self.nearest = {k: v for k, v in self.nearest.items() if k in nearby_foods}

    @staticmethod
    def merge(*dicts) -> dict:
        result = {}
        for d in dicts:
            for k, v in d.items():
                result[k] = result.get(k, []) + [v]
        return {k: sum(v) / len(v) for k, v in result.items()}

    @staticmethod
    def suggested_ele(d1):
        seen = []
        unseen = []
        weights = []
        for k, v in d1.items():
            if v:
                seen.append(k)
                weights.append(v)
            else:
                unseen.append(k)
        keys = seen + unseen

        if unseen:
            length = len(unseen)
            weights.extend([sum(weights) / length * 0.1111111111111111] * length)
        return random.choices(keys, weights)[0]

    @property
    def get(self) -> list:
        r = []

        while True:
            item = self.suggested_ele(self.nearest)
            if item in self.seen:
                continue

            self.seen.add(item)
            r.append(item)

            if len(r) == 6:
                break

        return sorted(r, key=lambda x: self.nearest[x], reverse=True)


def proceed() -> int:
    print("Do you want to proceed or retry?")
    return int(input("Enter 1 to Proceed or 2 to Retry: ")) == 1


if __name__ == '__main__':
    username = AccountManager().manage

    with open(f"Profiles/{username}.json") as f:
        user_data = json.load(f)

    while True:
        nearest = NearestNeighbors(username).get
        recommendations = RecommendationHandler(nearest).get

        clicks, impressions = DataCollector(recommendations)
        DataHandler(clicks, impressions)

        if proceed():
            break

    print("Loading Search Results...")
