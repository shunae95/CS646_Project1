from Transaction import Transaction

def cleanCreate(): # Generate a Transaction and create the file.
    _from = input("From: ")
    _to = input("To: ")
    _amount = input("Amount: ")
    x = Transaction(_from, _to, _amount)
    jsonString = x.toEncodedJSON()
    with open(jsonString+".json", "w") as f:
        f.write(x.toJSON())

def create(item:Transaction): # Create the file using premade Transaction.
    jsonString = item.toEncodedJSON()
    with open(jsonString+".json", "w") as f:
        f.write(item.toJSON())

if __name__ == "__main__":
    cleanCreate()