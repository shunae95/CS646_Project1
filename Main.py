"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-17
"""
import hashlib
import os
from Transaction import Transaction
from Block import Block
from wallet1.Wallet import Wallet as wallet_one
from wallet2.Wallet import Wallet as wallet_two
from wallet3.Wallet import Wallet as wallet_three

def main():

    # Instantiate 3 separate wallets, each with its own key pairs and address
    instantiate_wallets = input("Would you like to instantiate the 3 wallets? ").lower()

    if instantiate_wallets == "y" or addTransaction == "yes":
        wallet_1 = wallet_one()
        wallet_2 = wallet_two()
        wallet_3 = wallet_three()
        print(f"Wallet 1 address: {wallet_1.address}")
        print(f"Wallet 2 address: {wallet_2.address}")
        print(f"Wallet 3 address: {wallet_3.address}")
    
    dirName = os.path.dirname(__file__) # Variable to gain easy access to directory of current folder
    transactions = [] # Array that stores transactions
    addingTransactions = True # Variable that continues the loop if we are adding transactions
    try:
        os.mkdir(dirName + "\\processed") # Try to create the processed directory
    except FileExistsError:
        print("Processed folder exists.")
    try:
        os.mkdir(dirName + "\\pending") # Try to create the pending directory.
    except FileExistsError:
        print("Pending folder exists.")

    while addingTransactions: # Loop for adding transactions
        addTransaction = input("Would you like to add a transaction: ").lower()
        
        if addTransaction == "y" or addTransaction == "yes":
            newTransaction = Transaction()
            transactions.append(newTransaction)
        
        elif addTransaction != "y":
            for entry in transactions: # Loop that creates a json file for each transaction and moves it into pending folder
                with open(f"{entry.toEncodedJSON()}.json","w") as f:
                    f.write(entry.toJSON())
                os.rename((dirName+"\\"+entry.toEncodedJSON()+".json"), dirName+"\\pending\\"+ entry.toEncodedJSON()+".json")
            addingTransactions = False
    
    addingToBlock = True # Variable to manage the adding to the block loop
    height = 0 # Starting height 
    while addingToBlock:
        while os.path.exists(dirName + f"\\B_{height}.json"): # If a block at the current height exists, increment one
            height += 1 
        with open(f"B_{height}.json", "w") as f: 
            if height == 0: # If height is 0 then use the default previous hash
                block = Block(height, "NA")
            else: # Else use the hash of the previous block.
                with open(f"B_{height-1}.json", "rb") as oldBlock:
                    oldHash = hashlib.sha256(oldBlock.read()).hexdigest()
                block = Block(height, oldHash)
            
            for entry in transactions: # Add each pending transaction into the block's transaction array
                block.addTransaction(entry)

            block.completedTransactions = list(map(Transaction.toEncodedJSON, transactions))
            for file in os.scandir(dirName + "\\pending"):
                if file.name[:-5] in block.completedTransactions:
                    os.rename(dirName+"\\pending\\"+ file.name, dirName+"\\processed\\"+ file.name)

            f.write(block.generateData())
            
            addingToBlock = False

if __name__=="__main__":
    main()