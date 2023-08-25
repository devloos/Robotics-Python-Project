import json
import sys
from enum import Enum
import pandas as pd
from pandas import DataFrame
from dataclasses import dataclass


class MainOption(Enum):
    List = 1
    Add = 2
    Remove = 3
    Exit = 4


@dataclass
class Contact:

    name: str
    phoneNumber: str
    email: str
    relationship: str

    def __str__(self) -> str:

        strBuilder = ""
        strBuilder += f"Name: {self.name}\n"
        strBuilder += f"Phone Number: {self.phoneNumber}\n"
        strBuilder += f"Email: {self.email}\n"
        strBuilder += f"Relationship: {self.relationship}\n"

        return strBuilder


class Database:
    # Maintaining a copy of contacts since it would be expensive to go through
    # DataFrame and computing it every access
    contacts: list[Contact] = []
    df: DataFrame

    def __init__(self) -> None:
        try:
            self.df = pd.read_csv("db.csv")

            for index in self.df.index:
                contact = Contact()
                contact.name = self.df["Name"][index]
                contact.phoneNumber = self.df["Phone Number"][index]
                contact.email = self.df["Email"][index]
                contact.relationship = self.df["Relationship"][index]
                self.contacts.append(contact)
        except (IOError, ValueError):
            print()
            print("Database file not found!")
            print('File should be placed under the "db" folder.')
            sys.exit(1)

    def getContacts(self) -> list[Contact]:
        return self.contacts

    # take contact append it to contacts and update csv
    def addContact(self, contact: Contact):
        self.contacts.append(contact)
        obj = {
            "Name": [contact.name],
            "Phone Number": [contact.phoneNumber],
            "Email": [contact.email],
            "Relationship": [contact.relationship],
        }

        # create new DataFrame and append it to file hence mode="a"
        df = pd.DataFrame(obj)
        df.to_csv("db.csv", mode="a", index=False, header=False)

    # remove contact based on column and input
    def removeContact(self, name: str) -> None:
        # using local DataFrame snapshot to grab rows that passed condition
        localDf = self.df.loc[self.df["Name"] == name]

        if not localDf.empty:
            self.df.drop(localDf.index, inplace=True)
            self.df.to_csv("db.csv", index=False)
            self.contacts = filter(lambda el: el.name != name, self.contacts)

            # cant use join unfortunately since its under localDf.index
            result = "Dropped "
            for index in localDf.index:
                result += localDf["Name"][index]

            print(result + "!")


def main():

    try:
        filename = "config.json"

        try:
            file = open(filename)

            # result -> dict
            obj = dict(json.load(file))

            # validating that needed keys are in dict
            if "user" not in obj.keys():
                raise ValueError()
            elif "password" not in obj.keys():
                raise ValueError()
        except (IOError, ValueError):
            # fatal error give example config and exit
            print("Missing|Incorrect config.json file.")
            print("Example config:")
            print(json.dumps({"user": "xxxx", "password": "xxxxxxxxxx"}, indent=4))
            sys.exit(1)

        print(f"Hey {obj['user']}!\n")

        wrongPassword = True

        # repeat until correct password
        while wrongPassword:
            password = input("Please enter password: ")

            if obj["password"] != password:
                print("Wrong password try again!\n")
            else:
                wrongPassword = False

        db = Database()

        print()

        # main loop
        while True:
            try:
                print("1. List Contacts")
                print("2. Add Contact")
                print("3. Remove Contact")
                print("4. Exit\n")

                userInput = int(input("Option: "))
                option = MainOption(userInput)
            except ValueError:
                print("Invalid option try again!\n")
                continue

            print()
            match option:
                case MainOption.List:
                    for contact in db.getContacts():
                        print(contact)
                case MainOption.Add:
                    contact = Contact()
                    contact.name = input("Name: ")
                    contact.phoneNumber = input("Phone Number: ")
                    contact.email = input("Email: ")
                    contact.relationship = input("Relationship: ")
                    db.addContact(contact)
                    print()
                case MainOption.Remove:
                    userInput = input("Name: ")
                    db.removeContact(userInput)
                case other:
                    break
    except KeyboardInterrupt:
        pass

    file.close()


if __name__ == "__main__":
    main()
