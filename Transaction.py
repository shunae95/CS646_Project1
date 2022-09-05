from time import time
import hashlib

class Transaction:
    def __init__(self):
        self.sender = input("Sender: ") 
        self.recipient = input("Recipient: ")
        self.amount = float(input("Enter transaction amount: "))
        self.time = int(time())

    def toJSON(self):
        # Builds string in same format as example
        # {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        return "{" + f'"timestamp":{self.time},"from":"{self.sender}","to":"{self.recipient}","amount":{self.amount}' + "}"

    def toEncodedJSON(self):
        # Gets the JSON string and returns its SHA256 hash
        # Function turns string into bytes before hashing, then it follows up with hexdigest to turn it back into a string.
        # Input: {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        # Output: 57bc6f8255b180cbaf73f286b107be0506713b32cfe8f41af29e5c1e17f8ca6d
        return hashlib.sha256(str.encode(self.toJSON())).hexdigest()

if __name__ == "__main__":
    x = Transaction()
    print(x.toJSON())
    print(x.toEncodedJSON())












# import time
# import datetime
# import json
# import hashlib
# import os

# class Transaction:
#     def __init__(self):
#         self.sender = input("Sender: ")
#         self.recipient = input("Recipient: ")
#         self.amount = float(input("Enter transaction amount: "))
#         currentTime = datetime.datetime.now()
#         self.time = int(datetime.datetime.timestamp(currentTime)*1000)
#         self.data = "{" + f'"timestamp":{self.time},"from":"{self.sender}","to":"{self.recipient}","amount":{self.amount}' + "}"
#         return self



# def main(self):
    
#     transactions = []

#     while True:
#         addTransaction = input("Would you like to add a transaction: ")
        
#         if addTransaction == "y" or addTransaction == "yes":
#             newTransaction = Transaction()
#             print(newTransaction.data)
#             transactions.append(newTransaction.data)
#             print(transactions)
        
#         elif addTransaction != "y":
#             transactionJson = json.dumps(transactions)
        
#             with open("transactions.json","w") as outfile:
#                 json.dump(transactionJson, outfile)
        
#             filename = "transactions.json"
#             with open("transactions.json","rb") as f:
#                 file = f.read() 
#                 hash_text = hashlib.sha256(file).hexdigest()
#                 print(hash_text)

#             os.rename('transactions.json', f'{hash_text}.json')
#             return    
     
# if __name__=="__main__":
#     print(Transaction().sender)
#     # main(Transaction())