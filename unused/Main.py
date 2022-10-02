"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-17
"""
from distutils.log import error
from email.policy import default
import hashlib
import os
from Transaction import Transaction
from Block import Block
from wallet1.Wallet import Wallet
from wallet1.Wallet import Wallet as wallet_one
from wallet2.Wallet import Wallet as wallet_two
from wallet3.Wallet import Wallet as wallet_three

def transactionCreation():
    dirName = os.path.dirname(__file__) # Variable to gain easy access to directory of current folder
    # transactions = [] # Array that stores transactions
    # addingTransactions = True # Variable that continues the loop if we are adding transactions
    try:
        os.mkdir(dirName + "/processed") # Try to create the processed directory
    except FileExistsError:
        pass
        # print("Processed folder exists.")
    try:
        os.mkdir(dirName + "/pending") # Try to create the pending directory.
    except FileExistsError:
        pass
        # print("Pending folder exists.")


    newTransaction = Transaction()

    with open(f"{newTransaction.toEncodedJSON()}.json","w") as f:
        f.write(newTransaction.toJSON())
    os.rename((dirName+"/"+newTransaction.toEncodedJSON()+".json"), dirName+"/pending/"+ newTransaction.toEncodedJSON()+".json")

    return newTransaction


def grabPendingTransactions() -> list:
    transactions = []
    dirName = os.path.dirname(__file__)+"/pending"
    for file in os.scandir(dirName):
        with open(file.path, "r") as f:
            string = f.read()
            transaction = Transaction(string)
            transactions.append(transaction)
    
    transactions.sort(key=transactionSort)
    return transactions
    
def transactionSort(transaction: Transaction) -> int:
    return transaction.time

def processingToBlock():
    dirName = os.path.dirname(__file__)
    if len(list(os.scandir(dirName + "/pending"))) > 0:
        transactions = grabPendingTransactions()
        addingToBlock = True # Variable to manage the adding to the block loop
        height = 0 # Starting height 
        while addingToBlock:
            while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
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
                for file in os.scandir(dirName + "/pending"):
                    if file.name[:-5] in block.completedTransactions:
                        os.rename(dirName+"/pending/"+ file.name, dirName+"/processed/"+ file.name)

                f.write(block.generateData())
                
                addingToBlock = False 

def menu(userWallet: Wallet):
    present = True

    wallet_2 = wallet_two()
    wallet_3 = wallet_three()
    wallet_collection = [userWallet, wallet_2, wallet_3]

    while present:
        try:
            print("1. \tCheck local wallet balance.")
            print("2. \tCheck wallet balance using address.")
            print("3. \tCreate a transaction.")
            print("4. \tExit application.")

            response = int(input("> "))
            if (response == 1):
                balance = updateBalance(userWallet.address, wallet_collection)
                print(str(balance))
            elif (response == 2):
                searchedAccount = input("What is the address of the wallets balance you would like? ") 
                searchedAccountBalance = updateBalance(searchedAccount, wallet_collection)
                print(searchedAccountBalance)
            elif (response == 3):
                transaction = transactionCreation()
                updateBalance(transaction.recipient, wallet_collection, transaction)
                updateBalance(transaction.sender, wallet_collection, transaction)
            elif (response == 4):
                processingToBlock()
                print("Quitting application")
                present = False
        except:
            print("Invalid Input.")

def addOrSubtractTransaction(transaction, wallet_collection):

    for wallet in wallet_collection:
        if transaction == None:
            return
        elif transaction.recipient == wallet.address:
            wallet.balance = wallet.balance + transaction.amount
        elif transaction.sender == wallet.address:
            wallet.balance = wallet.balance - transaction.amount
        else:
            return wallet.balance


def updateBalance(searchedAccount, wallet_collection, transaction = None):

    for wallet in wallet_collection:
        if searchedAccount == wallet.address:
            break
        if transaction != None:
            if transaction.sender != wallet.address or transaction.sender != wallet.address:
                error_message = "This transaction can not be completed because recipient wallet can not be found"
                return error_message

    balance_dictionary = {}

    for wallet in wallet_collection:
        balance_dictionary[wallet.address] = wallet.balance

    addOrSubtractTransaction(transaction, wallet_collection)

    if (searchedAccount != None):
        if searchedAccount in balance_dictionary:
            account_balance = balance_dictionary[searchedAccount]            
            return "The account balance for wallet: " + str(searchedAccount) + " is " + str(account_balance)
        else:
            return "This does not exist"

def main():

    # Instantiate 3 separate wallets, each with its own key pairs and address
    wallet = Wallet()
    menu(wallet)

if __name__=="__main__":
    main()