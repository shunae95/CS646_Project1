import time
import datetime
import json
import hashlib
import os

class Transaction:
    def createTransaction(self):
        currentTime = datetime.datetime.now()
        self.time = datetime.datetime.timestamp(currentTime)*1000
        self.sender = input("Sender: ")
        self.recipient = input("Recipient: ")
        self.amount = float(input("Enter transaction amount: "))

        return self.time, self.sender, self.recipient, self.amount
        



def main(self):
    
    transactions = []

    while True:
        addTransaction = input("Would you like to add a transaction: ")
        
        if addTransaction == "y" or addTransaction == "yes":
            newTransaction = Transaction()
            transaction = newTransaction.createTransaction()
            print(transaction)
            transactions.append(transaction)
            print(transactions)
        
        elif addTransaction != "y":
            transactionJson = json.dumps(transactions)
        
            with open("transactions.json","w") as outfile:
                json.dump(transactionJson, outfile)
        
            filename = "transactions.json"
            with open("transactions.json","rb") as f:
                file = f.read() 
                hash_text = hashlib.sha256(file).hexdigest()
                print(hash_text)

            os.rename('transactions.json', f'{hash_text}.json')
            return    
     
if __name__=="__main__":
    main(Transaction())