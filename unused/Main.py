"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-17
"""
import hashlib
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from Transaction import Transaction
from Block import Block
from Wallet import Wallet, scanBlockchain
from Account import Account, searchForAccount
# from wallet1.Wallet import Wallet as wallet_one
# from wallet2.Wallet import Wallet as wallet_two
# from wallet3.Wallet import Wallet as wallet_three

def transactionCreation(userWallet: Wallet):
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


    newTransaction = Transaction(userWallet)
    # print(newTransaction.toBytes())
    transactionSignature = userWallet.signTransaction(newTransaction) 
    userWallet.pubkey.verify(transactionSignature, newTransaction.toBytes(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256()) #Verifies transaction with the public key
    with open(f"{newTransaction.toEncodedJSON()}.json","w") as f:
        f.write(newTransaction.toJSON())
    userWallet.account.pendingBalance -= newTransaction.amount #Subtract amount from pending balance
    print(f"Current balance for {userWallet.address}: {userWallet.account.balance} (Pending Balance: {userWallet.account.pendingBalance})")
    os.rename((dirName+"/"+newTransaction.toEncodedJSON()+".json"), dirName+"/pending/"+ newTransaction.toEncodedJSON()+".json")


def grabPendingTransactions() -> list:
    transactions = []
    dirName = os.path.dirname(__file__)+"/pending"
    for file in os.scandir(dirName):
        with open(file.path, "r") as f:
            string = f.read()
            transaction = Transaction(string)
            transactions.append(transaction)
    
    transactions.sort(key=transactionSort)
    # for i in transactions:
    #     print(i.time)
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
    print("Pending transctions added to block.")

def menu(userWallet: Wallet):
    present = True
    while present:
        try:
            print("1. \tCheck local wallet balance.")
            print("2. \tCheck wallet balance using address.")
            print("3. \tCreate a transaction.")
            print("4. \tProcess pending transactions to block.")
            print("5. \tExit application and process transactions.")

            response = int(input("> "))
            if (response == 1):
                # print("IMPLEMENT SHOWING PENDING BALANCE AS WELL, THIS WOULD REQUIRE UPADTING THE ACCOUNTS JSON PER TRANSACTION")
                # print("PENDING ONLY DISPLAYS OUTGOING AND DOES NOT CONSIDER INCOMING TRANSACTIONS")
                print(f"Current balance for {userWallet.address}: {userWallet.account.balance} (Pending Balance: {userWallet.account.pendingBalance})")
            elif (response == 2):
                address = input("Address: ")
                print(f"Current balance for {address}: {scanBlockchain(address)[0]}")
            elif (response == 3):
                transactionCreation(userWallet)
                # accountDB = updateAccountDB(userWallet.account)
                # rewriteAddressDatabase()
                # userWallet.balance, userWallet.latestBlock = scanBlockchain(userWallet.address) ?????? To update balance but latest block cannot really be updated since a newly created transaction will not be in a block yet
            elif (response == 4):
                processingToBlock() # Process Transaction into block
                userWallet.account.balance = userWallet.account.pendingBalance # Set pending balance to official balance
                updateAccountDB(userWallet.account) # Send account balance back to database
                # rewriteAddressDatabase()
            
            elif (response == 5):
                processingToBlock()
                userWallet.account.balance = userWallet.account.pendingBalance
                updateAccountDB(userWallet.account)
                # rewriteAddressDatabase()
                print("Quitting application.")
                present = False
        except InvalidSignature: 
            print("Invalid Signature for created transaction. Discarding transaction.")
        except:
            print("Invalid Input.")

def updateAccountDB(userAccount: Account):
    accountDB = Account.getAccList()
    for entry in accountDB:
        if userAccount.address == entry.address:
            entry.balance = userAccount.balance
            print("")
            # entry.pendingBalance = userAccount.balance
    file_path =  os.path.dirname(__file__) + "/Accounts.json"
    with open(file_path, "w") as f:
        for entry in accountDB:
            f.write("{"+f"{entry.address},{entry.publicKey()},{entry.balance}"+"}\n")
    return accountDB

def main():

    # Instantiate 3 separate wallets, each with its own key pairs and address
    accountDB = Account.getAccList()
        
    wallet = Wallet()

    if searchForAccount(wallet.address) != None: 
        wallet.account = searchForAccount(wallet.address)
    else:
        newAcc = Account(wallet.address, wallet.getPubKeyBytes().decode("utf-8"), scanBlockchain(wallet.address)[0])
        wallet.account = newAcc
        accountDB = newAcc.addAccToDB(accountDB)
        updateAccountDB(wallet.account)
    # wallet.account.balance = scanBlockchain(wallet.address)[0]

    menu(wallet)
    # instantiate_wallets = input("Would you like to instantiate the 3 wallets? ").lower()

    # if instantiate_wallets == "y" or addTransaction == "yes":
    #     wallet_1 = wallet_one()
    #     wallet_2 = wallet_two()
    #     wallet_3 = wallet_three()
    #     print(f"Wallet 1 address: {wallet_1.address}")
    #     print(f"Wallet 2 address: {wallet_2.address}")
    #     print(f"Wallet 3 address: {wallet_3.address}")
    
    
if __name__=="__main__":
    main()