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


### MISSING LOGIC ###
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

        for _ in range(min(14, len(self.foods) - 1)):
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


    def store_choices(self):
        local_dict = {}
        self.foods = DataCollector().foods
        for choice_tuple in self.choice_data:
            food1, food2 = choice_tuple

            if food1 in local_dict:
                local_dict[food1] += 1
            else:
                local_dict[food1] = (local_dict.get(food2, 2) + 1) // 2

            if food2 not in local_dict:
                data_collector.foods.append(food2)

        return list(local_dict.items())

    @staticmethod
    def update_global_from_local(local_dict, global_dict):
        for food, count in local_dict:

            # global_dict[food] = global_dict.get(food, 0) + count
            if food in global_dict:
                global_dict[food] += count
            else:
                global_dict[food] = count

        return global_dict


    def gather_and_update_choices(self, global_dict):
        local_dict = DataManager.store_choices(self)
        DataManager.update_global_from_local(local_dict, global_dict)
        return dict(sorted(global_dict.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def val_to_pct(dictionary):
        return {key: dictionary[key] / sum(dictionary.values()) * 100 for key in dictionary}


####### OTHER #######
class Others:
    @staticmethod
    def retry_choice():
        print("Do you want to re-try or continue?")
        return int(input("Enter 1 to Re-Try or 2 to Continue: ")) == 1

    ####################### GOOD ##########################
    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} to {n2} is {round(score * 100, 2)}% ({int(score * (n1+n2))}/{n1 + n2})."
    #######################################################
    # Create a new function to suggest items based on user's previous choices before updating gather_preferences and preference_exceptions.


if __name__ == '__main__':
    account_manager = AccountManager()
    username = account_manager.manage_account()

    with open(f"Profiles/{username}.json", "r") as f:
        global_dict = json.load(f)["global_dict"]

    data_collector = DataCollector()
    choice_data = data_collector.gather_preferences()

    data_manager = DataManager(choice_data)

    others = Others()

    while True:
        global_dict = data_manager.gather_and_update_choices(
            choice_data)

        global_pct_dict = data_manager.val_to_pct(global_dict)

        print(data_collector.foods)
        # Either implement a reset function for dictionaries or  improve the current logic (the latter being more challenging but superior).

        with open(f"Profiles/{username}.json", "r+") as f:
            account = json.load(f)
            account["global_dict"] = global_dict
            account["global_pct_dict"] = global_pct_dict
            f.seek(0)
            json.dump(account, f, indent=4, separators=(',', ': '))
            f.truncate()

        retry = others.retry_choice()
        # Add functionality to update values in JSON file, reset food list, and improve suggestions on re-run.

        if retry:
            continue
        break

    print(global_dict)
    print()
    print(global_pct_dict)
