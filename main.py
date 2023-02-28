import json
import random


class AccountManager:
    @staticmethod
    def signup():
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        account = {username: password,
                   "global_dict": {}, "global_pct_dict": {}}

        with open(f"Profiles/{username}.json", "w") as f:
            json.dump(account, f, indent=4, separators=(',', ': '))

        print("Account created successfully!")
        return username

    @staticmethod
    def login():
        for _ in range(3):
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            try:
                with open(f"Profiles/{username}.json", "r") as f:
                    account = json.load(f)

                if account[username] == password:
                    return username
            except (FileNotFoundError, KeyError):
                print("Could not load profile.")

            print("Invalid username/password combination.")

        print("You've exceeded the number of login attempts.")
        raise SystemExit

    def manage_account(self):
        while True:
            choice = input(
                "Enter '1' to create a new account or '2' to login to an existing one: ")

            if choice == '1':
                return AccountManager.signup()
            elif choice == '2':
                return AccountManager.login()
            else:
                print("Invalid choice. Please enter '1' or '2'.")


class PreferenceCollector:
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

    def preference(self, option1, option2):
        print(f"Do you prefer: {option1} or {option2}?")
        return int(input("Enter 1 for the first option or 2 for the second: "))

    def gather_preferences(self):
        pref_hist = []
        option1 = random.choice(self.options_list)

        for _ in range(min(14, len(self.options_list) - 1)):
            option2 = random.choice(
                [option for option in self.options_list if option != option1]
            )
            choice = self.preference(option1, option2)

            if choice == 2:
                option1, option2 = option2, option1

            pref_hist.append((option1, option2))
            self.options_list.remove(option2)

        self.options_list.remove(option1)
        return pref_hist


class DataManager:
    def __init__(self, pref_hist):
        self.pref_hist = pref_hist
        self.pref_dict = {}
        self.non_pref_list = []

    def convert_choice_data(self):
        for choice_tuple in self.pref_hist:
            preferred, non_preferred = choice_tuple

            if preferred not in self.pref_dict:
                self.pref_dict[preferred] = self.pref_dict.get(
                    non_preferred, 0) + 1
            else:
                self.pref_dict[preferred] += 1

            if non_preferred not in self.pref_dict:
                self.non_pref_list.append(non_preferred)

        return list(self.pref_dict.items())

    @staticmethod
    def combine_dictionaries(d1, d2):
        for food, count in d1:
            d2[food] = d2.get(food, 0) + count

        return dict(sorted(d2.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def convert_values_to_percentage(dict):
        return {key: dict[key] / sum(dict.values()) * 100 for key in dict}

    @staticmethod
    def save_profile_data(profile, global_dict, global_pct_dict, profile_file):
        profile["global_dict"] = global_dict
        profile["global_pct_dict"] = global_pct_dict

        with open(profile_file, "w") as f:
            json.dump(profile, f, indent=4, separators=(',', ': '))


class Other:
    @staticmethod
    def choose_to_proceed():
        print("Do you want to re-try or proceed?")
        return int(input("Enter 1 to Re-Try or 2 to Proceed: ")) == 1

    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} to {n2} is {round(score * 100, 2)}% ({int(score * (n1 + n2))}/{n1 + n2})."


if __name__ == '__main__':
    account_manager = AccountManager()
    username = account_manager.manage_account()

    profile_file = f"Profiles/{username}.json"
    with open(profile_file, "r") as f:
        profile = json.load(f)

    global_dict = profile["global_dict"]

    pref_collector = PreferenceCollector()
    pref_hist = pref_collector.gather_preferences()

    data_manager = DataManager(pref_hist)
    local_dict = data_manager.convert_choice_data()
    global_dict = data_manager.combine_dictionaries(local_dict, global_dict)
    global_pct_dict = data_manager.convert_values_to_percentage(global_dict)
    data_manager.save_profile_data(profile, global_dict,
                                   global_pct_dict, profile_file)

    others = Other()
    while proceed := others.choose_to_proceed():
        pref_hist = pref_collector.gather_preferences()
        local_dict = data_manager.convert_choice_data()
        global_dict = data_manager.combine_dictionaries(
            local_dict, global_dict)
        global_pct_dict = data_manager.convert_values_to_percentage(
            global_dict)

        data_manager.save_profile_data(
            profile, global_dict, global_pct_dict, profile_file)
