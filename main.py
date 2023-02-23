import json
import random


class Session:
    foods = [
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
                    print("Login successful!")
                    return username
                else:
                    print("Invalid username/password combination.")
            except FileNotFoundError:
                print("Account does not exist.")

            username = None
            password = None

        print("You've exceeded the number of login attempts.")
        raise SystemExit

    @staticmethod
    def preference(first_option, second_option):
        print(f"Do you prefer: {first_option} or {second_option}?")
        return int(input("Enter 1 for the first option or 2 for the second: "))

    def preference_exceptions(self, username):
        try:
            with open(f"Profiles/{username}.json", "r") as f:
                global_dict = json.load(f)["global_dict"]
        except FileNotFoundError as e:
            raise SystemExit(f"Error: {e}. File not found.") from e
        else:
            global_dict_copy = list(global_dict.keys())

        if not global_dict_copy:
            raise ValueError("Error: global_dict list is empty.")

        for _ in range(14 - self.list_length):
            second_food = [
                food for food in global_dict_copy if food != first_food
            ]

            if not second_food:
                break  # No more food options available

            choice = self.preference(first_food, second_food)

            if choice == 2:
                first_food, second_food = second_food, first_food

            choice_data.append((first_food, second_food))
            self.foods.remove(second_food)

    def gather_preferences(self):
        choice_data = []
        first_food = random.choice(self.foods)
        self.list_length = len(self.foods) - 1

        for _ in range(min(14, self.list_length)):
            second_food = random.choice(
                [food for food in self.foods if food != first_food]
            )
            choice = self.preference(first_food, second_food)

            if choice == 2:
                first_food, second_food = second_food, first_food

            choice_data.append((first_food, second_food))
            self.foods.remove(second_food)

        if self.list_length < 14:
            self.preference_exceptions(username)

        self.foods.remove(first_food)
        return choice_data

    @staticmethod
    def store_choices(choice_data):
        local_dict = {}
        for choice_tuple in choice_data:
            food1, food2 = choice_tuple

            if food1 in local_dict:
                local_dict[food1] += 1
            else:
                local_dict[food1] = (local_dict.get(food2, 2) + 1) // 2

            if food2 not in local_dict:
                Session.foods.append(food2)

        return local_dict

    @staticmethod
    def update_global(local_dict, global_dict):
        for food, count in local_dict.items():
            global_dict[food] = global_dict.get(food, 0) + count

        return dict(sorted(global_dict.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def val_to_pct(dict):
        return {key: dict[key] / sum(dict.values()) * 100 for key in dict}

    @staticmethod
    def retry_choice():
        print("Do you want to re-try or continue?")
        return int(input("Enter 1 to Re-Try or 2 to Continue: ")) == 1

    @staticmethod
    def calculate_similarity(n1, n2):
        score = 1 - abs(n1 - n2) / (n1 + n2)
        return f"The similarity of {n1} to {n2} is {round(score * 100, 2)}% ({int(score * (n1+n2))}/{n1 + n2})."

    # Before updating gather_preferences and preference_exceptions, create a new function to suggest items based on user's previous choices.


if __name__ == '__main__':
    ActiveSession = Session()

    while True:
        choice = input(
            "Enter '1' to create a new account or '2' to login to an existing one: ")
        if choice == '1':
            username = ActiveSession.signup()  # Add Confirmation
            break
        elif choice == '2':
            username = ActiveSession.login()
            break
        else:
            print("Invalid choice. Please enter '1' or '2'.")

    try:
        with open(f"Profiles/{username}.json", "r") as f:
            global_dict = json.load(f)["global_dict"]
    except FileNotFoundError as e:
        raise SystemExit from e

    while True:
        choice_data = ActiveSession.gather_preferences()
        local_dict = ActiveSession.store_choices(choice_data)
        global_dict = ActiveSession.update_global(local_dict, global_dict)
        global_pct_dict = ActiveSession.val_to_pct(global_dict)

        print(ActiveSession.foods)
        # Add functionality to reset dictionaries.

        retry = ActiveSession.retry_choice()
        # Add functionality to update values in JSON file, reset food list, and improve suggestions on rerun.

        with open(f"Profiles/{username}.json", "r+") as f:
            account = json.load(f)
            account["global_dict"] = global_dict
            account["global_pct_dict"] = global_pct_dict
            f.seek(0)
            json.dump(account, f, indent=4, separators=(',', ': '))
            f.truncate()

        if retry:
            continue
        break

    print(global_dict)
    print()
    print(global_pct_dict)
