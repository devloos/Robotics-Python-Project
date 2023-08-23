import json
import sys
from enum import Enum
import pandas as pd
from pandas import DataFrame


class MainOption(Enum):
    List = 1
    Add = 2
    Remove = 3
    Sort = 4
    Exit = 5


class Contact:
    name: str
    phoneNumber: str
    email: str
    relationship: str

    def __init__(self) -> None:
        pass

    def setName(self, name: str) -> None:
        self.name = name

    def getName(self) -> str:
        return self.name

    def setPhoneNumber(self, phoneNumber: str) -> None:
        self.phoneNumber = phoneNumber

    def getPhoneNumber(self) -> str:
        return self.phoneNumber

    def setEmail(self, email: str) -> None:
        self.email = email

    def getEmail(self) -> str:
        return self.email

    def setRelationship(self, relationship: str) -> None:
        self.relationship = relationship

    def getRelationship(self) -> str:
        return self.relationship

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
            self.df = pd.read_csv("db/example.csv")

            for index in self.df.index:
                contact = Contact()
                contact.setName(self.df["Name"][index])
                contact.setPhoneNumber(self.df["Phone Number"][index])
                contact.setEmail(self.df["Email"][index])
                contact.setRelationship(self.df["Relationship"][index])
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
            "Name": [contact.getName()],
            "Phone Number": [contact.getPhoneNumber()],
            "Email": [contact.getEmail()],
            "Relationship": [contact.getRelationship()],
        }

        # create new DataFrame and append it to file hence mode="a"
        df = pd.DataFrame(obj)
        df.to_csv("db/example.csv", mode="a", index=False, header=False)

    # remove contact based on column and input
    def removeContact(self, removeInput: str, column: str) -> str | None:
        # using local DataFrame snapshot to grab rows that passed condition
        localDf = self.df.loc[self.df[column] == removeInput]

        if localDf.empty:
            return None
        else:
            self.df.drop(localDf.index, inplace=True)
            self.df.to_csv("db/example.csv", index=False)

            # cant use join unfortunately since its under localDf.index
            result = "Dropped "
            for index in localDf.index:
                result += localDf["Name"][index]

            return result + "!"

    def sortByName(self):
        self.contacts.sort(key=lambda el: el.getName())
        self.df = self.df.sort_values(by=["Name"], ascending=True)
        self.df.to_csv("db/example.csv", index=False)


# STARTING POINT
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
            print("4. Sort Contacts By Name")
            print("5. Exit\n")

            userInput = int(input("Option: "))
            option = MainOption(userInput)
        except ValueError:
            print("Invalid option try again!\n")
            continue

        match option:
            case MainOption.List:
                for contact in db.getContacts():
                    print(contact)
            case MainOption.Add:
                contact = Contact()
                contact.setName(input("Name: "))
                contact.setPhoneNumber(input("Phone Number: "))
                contact.setEmail(input("Email: "))
                contact.setRelationship(input("Relationship: "))
                db.addContact(contact)
                print()
            case MainOption.Remove:
                userInput = input("Name: ")
            case MainOption.Sort:
                db.sortByName()
            case other:
                break
except KeyboardInterrupt:
    pass

file.close()
# ENDING POINT
