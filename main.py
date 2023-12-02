import json
import os
import random


# Implement TensorFlow recommendations instead of static methods.
nearby_foods = {"avocado toast", "burritos", "chicken and rice", "chicken stir fry", "chicken wings", "crab legs", 
                "crêpes", "dumplings", "french toast", "gnocchi", "grilled oysters", "grilled salmon", "hamburgers", 
                "lobster tail", "pizza", "quesadillas", "ramen noodles", "shrimp scampi", "smoothies", "soup", 
                "spaghetti & meatballs", "steak", "steamed clams", "sushi", "tacos", "waffles"}


class AccountManager:
    @staticmethod
    def signup() -> str:
        for _ in range(3):
            USER = input("Enter a username: ")
            if os.path.exists(f"Profiles/{USER}.json"):
                print("Username already exists.")
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

            file_path = f"Profiles/{USER}.json"
            if os.path.exists(file_path) and json.load(open(file_path)).get(USER) == PASS:
                return USER
            else:
                print("Incorrect username or password.")

        print("You've exceeded the number of login attempts.")
        raise SystemExit

    def interaction(self) -> str:
        for i in range(3):
            var = input("Enter '1' to create an account or '2' to login to an existing one: ")
            if var == '1':
                return self.signup()
            elif var == '2':
                return self.login()
            elif i < 2:
                print("Invalid choice. Please enter '1' or '2'.")

        print("Raising SystemExit")
        raise SystemExit

    @property
    def manage(self) -> str:
        return self.interaction()


class DataCollector:
    def __init__(self, r: list):
        self.clicks = {}
        self.impressions = {}
        self.recommendations = r
        self.collect_data()

    @staticmethod
    def arrange(a: str, b: str) -> tuple:
        print(f"\nDo you prefer: {a} or {b}?")
        return (a, b) if input(f"Enter 1 for {a} or 2 for {b}: ") == "1" else (b, a)

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
        self.store_changes()

    @staticmethod
    def merge(d1: dict, d2: dict) -> dict:
        for k, v in d1.items():
            d2[k] = d2.get(k, 0) + v

        return d2

    @staticmethod
    def calculate_cpi(d1: dict, d2: dict) -> dict:
        d3 = {}
        for k in d1:
            if d1[k] == 0 or d2[k] == 0:
                d3[k] = 0
            else:
                d3[k] = d1[k] / d2[k] * 100

        return d3

    def store_changes(self):
        user_data.update(clicks=self.clicks,
                         impressions=self.impressions,
                         cpi=self.calculate_cpi(self.clicks, self.impressions))

        with open(f"Profiles/{username}.json", "w") as file:
            json.dump(user_data, file, indent=4, separators=(',', ': '))


class NearestNeighbors:
    def __init__(self, name: str):
        self.directory = os.listdir('Profiles/')
        self.k_neighbors = round(len(self.directory) ** 0.6666666666666666)
        self.directory.remove(f'{name}.json')

    @staticmethod
    def calculate_difference(d1: dict, d2: dict) -> float:
        shared_keys = d1.keys() & d2.keys()
        if not shared_keys:
            return 0.0

        key_difference_sum = sum(abs(d1[k] - d2[k]) for k in shared_keys)
        return key_difference_sum / len(shared_keys)

    def retrieve_profile(self) -> dict:
        random_file = random.choice(self.directory)
        self.directory.remove(random_file)

        with open(f"Profiles/{random_file}") as file:
            json_data = json.load(file)

        return json_data["cpi"]

    @property
    def fetch(self) -> list:
        dicts = []
        scores = []
        for _ in range(self.k_neighbors):
            json_data = self.retrieve_profile()
            dicts.append(json_data)
            similarity = self.calculate_difference(json_data, user_data["cpi"])
            scores.append(similarity)

        return sorted(dicts, key=lambda x: scores[dicts.index(x)])[:3]


class RecommendationHandler:
    def __init__(self, nearest_neighbors: list):
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
    def calculate_values(d1: dict) -> tuple:
        seen = []
        unseen = []
        weights = []
        for k, v in d1.items():
            if v != 0:
                seen.append(k)
                weights.append(v)
            else:
                unseen.append(k)

        keys = seen + unseen

        if unseen:
            length = len(unseen)
            weights.extend([sum(weights) / length * 0.2222222222222222] * length)

        return keys, weights

    @staticmethod
    def generate_suggestions(keys: list, weights: list) -> list:
        selected_keys = set()
        while len(selected_keys) < 6:
            selected_keys.add(random.choices(keys, weights)[0])

        return list(selected_keys)

    @property
    def fetch(self) -> list:
        keys, weights = self.calculate_values(self.nearest)
        return self.generate_suggestions(keys, weights)


def proceed() -> int:
    print("\nDo you want to proceed or retry?")
    return input("Enter 1 to Proceed or 2 to Retry: ") == "1"


if __name__ == '__main__':
    try:
        username = AccountManager().manage

        with open(f"Profiles/{username}.json") as f:
            user_data = json.load(f)

        while True:
            nearest = NearestNeighbors(username).fetch
            recommendations = RecommendationHandler(nearest).fetch
            clicks, impressions = DataCollector(recommendations)
            DataHandler(clicks, impressions)

            if proceed():
                break

        print("\nLoading Search Results...")

    except KeyboardInterrupt:
        raise SystemExit
