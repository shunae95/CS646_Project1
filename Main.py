import json
import hashlib
import os
from Transaction import Transaction

def main():
    
    transactions = []

    while True:
        addTransaction = input("Would you like to add a transaction: ")
        
        if addTransaction == "y" or addTransaction == "yes":
            newTransaction = Transaction()
            transaction = newTransaction.createTransaction()
            transactions.append(transaction)
        
        elif addTransaction != "y":
            transactionJson = json.dumps(transactions)        
            with open("transactions.json","w") as outfile:
                json.dump(transactionJson, outfile)
        
            filename = "transactions.json"
            with open("transactions.json","rb") as f:
                file = f.read() 
                hash_text = hashlib.sha256(file).hexdigest()

            os.rename('transactions.json', f'{hash_text}.json')
            return    
     
if __name__=="__main__":
    main()