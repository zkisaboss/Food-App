import json
import random


####### CLEAN #######
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


####### CLEAN #######
class DataCollector:
    def __init__(self):
        self.foods = [
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

    def preference(self, first_option, second_option):
        print(f"Do you prefer: {first_option} or {second_option}?")
        return int(input("Enter 1 for the first option or 2 for the second: "))

    def gather_preferences(self):
        choice_data = []
        first_food = random.choice(self.foods)

        for _ in range(min(4, len(self.foods) - 1)):
            second_food = random.choice(
                [food for food in self.foods if food != first_food]
            )
            choice = self.preference(first_food, second_food)

            if choice == 2:
                first_food, second_food = second_food, first_food

            choice_data.append((first_food, second_food))
            self.foods.remove(second_food)

        self.foods.remove(first_food)
        return choice_data


####### MESSY #######
class DataManager:
    def __init__(self, choice_data):
        self.choice_data = choice_data
        self.food_dict = {}
        self.food_storage = []

    def store_choices(self):
        for choice_tuple in self.choice_data:
            food1, food2 = choice_tuple

            if food1 not in self.food_dict:
                self.food_dict[food1] = self.food_dict.get(food2, 0) + 1
            else:
                self.food_dict[food1] += 1

            if food2 not in self.food_dict:
                self.food_storage.append(food2)

        return list(self.food_dict.items())

    @staticmethod
    def update_profile_dict(organized_foods, profile_dict):
        for food, count in organized_foods:
            if food in profile_dict:
                profile_dict[food] += count
            else:
                profile_dict[food] = count

        return dict(sorted(profile_dict.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def val_to_pct(global_dict):
        return {key: global_dict[key] / sum(global_dict.values()) * 100 for key in global_dict}

    @staticmethod
    def save_profile(profile, global_dict, global_pct_dict, profile_file):
        profile["global_dict"] = global_dict
        profile["global_pct_dict"] = global_pct_dict

        with open(profile_file, "w") as f:
            json.dump(profile, f, indent=4, separators=(',', ': '))


####### OTHER #######
class Other:
    @staticmethod
    def proceed_choice():
        print("Do you want to re-try or proceed?")
        return int(input("Enter 1 to Re-Try or 2 to Proceed: ")) == 1

    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} to {n2} is {round(score * 100, 2)}% ({int(score * (n1+n2))}/{n1 + n2})."


if __name__ == '__main__':
    # Initialize account manager and get the username
    account_manager = AccountManager()
    username = account_manager.manage_account()

    # Load the profile for the user
    profile_file = f"Profiles/{username}.json"
    with open(profile_file, "r") as f:
        profile = json.load(f)

    # Get the global dictionary from the profile and print it
    global_dict = profile["global_dict"]
    print(f"Global Dict: {global_dict}")

    # Collect choice data and print it
    data_collector = DataCollector()
    choice_data = data_collector.gather_preferences()
    print(f"Choice Data: {choice_data}")

    # Store the choice data in local dictionary and update the global dictionaries
    data_manager = DataManager(choice_data)
    local_dict = data_manager.store_choices()
    global_dict = data_manager.update_profile_dict(local_dict, global_dict)
    global_pct_dict = data_manager.val_to_pct(global_dict)
    data_manager.save_profile(profile, global_dict,
                              global_pct_dict, profile_file)

    # Ask user if they want to continue gathering choice data
    others = Other()
    while proceed := others.proceed_choice():
        # Gather choice data and update dictionaries
        choice_data = data_collector.gather_preferences()
        local_dict = data_manager.store_choices()
        global_dict = data_manager.update_profile_dict(local_dict, global_dict)
        global_pct_dict = data_manager.val_to_pct(global_dict)

        # Update user's profile with new dictionaries
        data_manager.save_profile(
            profile, global_dict, global_pct_dict, profile_file)

    # Print the final dictionaries
    print()
    print(global_dict)
    print()
    print(global_pct_dict)
