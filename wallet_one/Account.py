import os


class Account:
    def __init__(self, *args):
        if (len(args) == 3):
            self.address = args[0]
            self.__publicKey = args[1]
            self.balance = float(args[2])
            self.pendingBalance = float(args[2])
            
        else:
            accountString = args[0]
            array = accountString.split("}")

            self.address = array[0]
            self.__publicKey = array[1]
            self.balance = float(array[2])
            self.pendingBalance = float(array[2])
            # print(f"Address: {self.address}    PubKey: {self.__publicKey}     Balance: {self.balance}")
    
    def publicKey(self):
        return self.__publicKey

    def addAcc(self):
        self.getAccDB()
        file_path =  os.path.dirname(os.path.dirname(__file__)) + "/Accounts.json"
        alreadyAdded = False
        accountLine = "{" + f"{self.address},{self.__publicKey},{self.balance}" + "}"
        with open(file_path, "r") as f:
            if accountLine in f.read():
                alreadyAdded = True
        if not alreadyAdded:
            with open(file_path, "a") as f:
                f.write(accountLine+"\n")

    def createAccDB(self):
        file_path =  os.path.dirname(os.path.dirname(__file__)) + "/Accounts.json"
        with open(file_path, "w") as f:
            db = ""
            f.write(db)

    def getAccDB(self) -> str:
        file_path =  os.path.dirname(os.path.dirname(__file__)) + "/Accounts.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                db = f.read()
        else:
            self.createAccDB()
            db = ""
        return db

    def addAccToDB(self, list:list) -> list:
        list.append(self)
        self.addAcc()
        return list
    @staticmethod
    def getAccList() -> list:
        accounts = []
        file_path =  os.path.dirname(os.path.dirname(__file__)) + "/Accounts.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                accountEntries = f.read().split("}")
                for entry in accountEntries:
                    accountComponents = entry.strip("{").split(",")
                    # print(accountComponents)
                    if (len(accountComponents) == 3):
                        # print("entry.name: " + accountComponents[0].lstrip('\n{'))
                        accounts.append(Account(accountComponents[0].lstrip("\n{"), accountComponents[1], accountComponents[2]))

        return accounts


# def rewriteAddressDatabase():
#     accountDB = Account.getAccList()
#     file_path =  os.path.dirname(__file__) + "/AccountsD.json"
#     with open(file_path, "w") as f:
#         for entry in accountDB:
#             f.write("{"+f"{entry.address},{entry.publicKey()},{entry.balance}"+"}\n")

def searchForAccount(address:str) -> Account:
    accounts = Account.getAccList()
    for entry in accounts:
        if (entry.address == address):
            return entry
    return None

if __name__ == "__main__":
    print(searchForAccount("4e53d471dea8901c95b7310a37dd9bbf0e9dfb880a030b08b0d1199978e36a59"))