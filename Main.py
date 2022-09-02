import json
import hashlib
import os
from Transaction import Transaction

def main():
    
    transactions = []

    while True:
        addTransaction = input("Would you like to add a transaction: ").lower()
        
        if addTransaction == "y" or addTransaction == "yes":
            newTransaction = Transaction()
            transaction = newTransaction.createTransaction()
            transactions.append(transaction)
        
        elif addTransaction != "y":
            for entry in transactions:
                hash = hashlib.sha256(str.encode(entry)).hexdigest()
                with open(f"{hash}.json","w") as f:
                    f.write(entry)

            return    
     
if __name__=="__main__":
    main()