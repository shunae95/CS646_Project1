"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-21

Code samples taken from python cryptography package documentation at https://cryptography.io/en/latest/.
"""
import os
import sys
from os.path import exists
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import base64


from Transaction import Transaction
from Block import Block
from Account import Account, searchForAccount



class Wallet:
    """
    Creates an instance of a wallet. Will read the wallet's existing private key
    or create a new one if one does not already exist.
    """
    def __init__(self):
        pw = 'mypassword' # No password needed at this stage in the project, so default set
        self.password = pw.encode("utf-8")
        self.dirName = os.path.dirname(__file__) # Get current folder
        self.pemFileName = f"{self.dirName}/privkey.pem" 
        self.__privkey = self.getOrCreatePem() 
        self.pubkey = self.__privkey.public_key()
        self.pubkey_bytes = self.getPubKeyBytes() # May not need this since we don't have to store it
        self.address = self.getOrCreateAddress()
        
        self.account = None
        

    def createPem(self):
        """
        Create new private key and save it as PEM in file privkey.pem"""
        private_key = rsa.generate_private_key(
            public_exponent=65537, 
            key_size=2048,
        )
        pem = private_key.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(self.password)
        )
        
        with open(self.pemFileName,"wb") as f:
            f.write(pem)

    def getOrCreatePem(self):      
        """
        Check to see if private key already exists. 
        If it does not, call createPem() to create a new one."""
        if exists(self.pemFileName) == False:
            self.createPem()
        with open(self.pemFileName,"rb") as f:
            privkey = serialization.load_pem_private_key(
            f.read(),
            password=self.password,
            )
        return privkey

    def getPubKeyBytes(self):
        pubkey_bytes = self.pubkey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
        )
        return pubkey_bytes

    def getOrCreateAddress(self):
        addr = hashlib.sha256(base64.b64decode(self.pubkey_bytes)).hexdigest()
        return addr

    '''
    Returns the signature from the transaction being signed by the private key.
    '''
    def signTransaction(self, transaction):
        signature = self.__privkey.sign(transaction.toBytes(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        return signature

'''
Function will check each block for the address and add/subtract the amounts found in transactions

TODO: Decide whether or not the user is denied the transaction upon creation if the amount in the account is less than what is present
      or let user place transaction and then be denied during the block creation.

      Assuming this is the case, if so then it must be implemented... Subtract from user's account (maybe make a pending account) in the wallet class that holds their
      amount and does calculation during process.

      Add a feature that will keep a last block looked at for the account, so when the user needs to look at their account, calculations can be picked up from the last
      block, rather than starting from scratch.
'''
def scanBlockchain(address: str) -> tuple:
    balance = 0
    latestBlock = 0
    dirName = os.path.dirname(os.path.dirname(__file__))
    for file in os.scandir(dirName):
        if file.name.startswith("B_") and file.name.endswith(".json"):
            # print(file.name)
            blockNumber = int(file.name.lstrip("B_").rstrip(".json"))
            if blockNumber > latestBlock:
                latestBlock = blockNumber
            with open(file.path, "r") as f:
                jsonString = f.read()
            jsonSplit = " ".join(jsonString.split("\"body\":"))
            contentSplit = jsonSplit.split("\"content\":")

            for i in range(len(contentSplit)):
                if i == 0: 
                    # print(f"Number of trnx: {len(contentSplit)-1}")
                    continue
                elif i < len(contentSplit)-1:
                    contentSplit[i] = contentSplit[i].split("},{\"hash\"")[0]
                else:
                    contentSplit[i] = contentSplit[i].split("}]}")[0]
                
                fromToFields = contentSplit[i].split(",")[1:3]
                fromField = fromToFields[0].split(":")[1].strip('"')
                toField = fromToFields[1].split(":")[1].strip('"')
                amountField = float(contentSplit[i].split(",")[3].split(":")[1].strip("}"))
                # print(f"From: {fromField}, To: {toField}, Amount: {amountField}")
                if fromField == address:
                    balance -= amountField
                elif toField == address:
                    balance += amountField
    # print(f"Final Balance for {address}: {balance}")
    return (balance, latestBlock)


'''
Not used, but would returned a selected account from the database if it matched the address
'''
# def scanBlockchainDB(address:str, accountDB:list) -> Account:
#     for entry in accountDB:
#         if entry.address == address:
#             return entry
#     return None

def transactionCreation(userWallet: Wallet):
    dirName = os.path.dirname(os.path.dirname(__file__)) # Variable to gain easy access to directory of current folder
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
    with open(f"{dirName}/{newTransaction.toEncodedJSON()}.json","w") as f:
        f.write(newTransaction.toJSON())
    userWallet.account.pendingBalance -= newTransaction.amount #Subtract amount from pending balance
    print(f"Current balance for {userWallet.address}: {userWallet.account.balance} (Pending Balance: {userWallet.account.pendingBalance})")
    os.rename((dirName+"/"+newTransaction.toEncodedJSON()+".json"), dirName+"/pending/"+ newTransaction.toEncodedJSON()+".json")


def grabPendingTransactions() -> list:
    transactions = []
    dirName = os.path.dirname(os.path.dirname(__file__))+"/pending"
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
    dirName = os.path.dirname(os.path.dirname(__file__))
    if len(list(os.scandir(dirName + "/pending"))) > 0:
        transactions = grabPendingTransactions()
        addingToBlock = True # Variable to manage the adding to the block loop
        height = 0 # Starting height 
        while addingToBlock:
            while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
                height += 1 
            with open(f"{dirName}/B_{height}.json", "w") as f: 
                if height == 0: # If height is 0 then use the default previous hash
                    block = Block(height, "NA")
                else: # Else use the hash of the previous block.
                    with open(f"{dirName}/B_{height-1}.json", "rb") as oldBlock:
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
        # try:
            print("1. \tCheck local wallet balance.")
            print("2. \tCheck wallet balance using address.")
            print("3. \tCreate a transaction.")
            print("4. \tProcess pending transactions to block.")
            print("5. \tExit application and process transactions.")

            response = int(input("> "))
            if (response == 1):
                # print("IMPLEMENT SHOWING PENDING BALANCE AS WELL, THIS WOULD REQUIRE UPADTING THE ACCOUNTS JSON PER TRANSACTION")
                # print("PENDING ONLY DISPLAYS OUTGOING AND DOES NOT CONSIDER INCOMING TRANSACTIONS")
                if userWallet.account.balance != scanBlockchain(userWallet.address)[0]:
                    userWallet.account.balance = scanBlockchain(userWallet.address)[0]
                    userWallet.account.pendingBalance = userWallet.account.balance
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
                # userWallet.account.balance = userWallet.account.pendingBalance # Set pending balance to official balance
                userWallet.account.balance = scanBlockchain(userWallet.address)[0]
                userWallet.account.pendingBalance = userWallet.account.balance
                updateAccountDB(userWallet.account) # Send account balance back to database
                # rewriteAddressDatabase()
            
            elif (response == 5):
                processingToBlock()
                
                # userWallet.account.balance = userWallet.account.pendingBalance
                userWallet.account.balance = scanBlockchain(userWallet.address)[0]
                userWallet.account.pendingBalance = userWallet.account.balance
                updateAccountDB(userWallet.account)
                # rewriteAddressDatabase()
                print("Quitting application.")
                present = False
        # except InvalidSignature : 
        #     print("Invalid Signature for created transaction. Discarding transaction.")
        # except:
        #     print("Invalid Input.")

def updateAccountDB(userAccount: Account):
    accountDB = Account.getAccList()
    for entry in accountDB:
        # print(f"{userAccount.address} - {entry.address}")
        if userAccount.address == entry.address:
            entry.balance = userAccount.balance
        else:
            entry.balance = scanBlockchain(entry.address)[0]
            # entry.pendingBalance = userAccount.balance
    file_path =  os.path.dirname(os.path.dirname(__file__)) + "/Accounts.json"
    with open(file_path, "w") as f:
        for entry in accountDB:
            addressLine = "{" +f"{entry.address},{entry.publicKey()},{entry.balance}"+"}\n"
            if addressLine.startswith("{\n"):
                addressLine = "{" + addressLine.lstrip("{\n")
            # print(f"{userAccount.balance}-{entry.balance}")
            # print(addressLine)
            f.write(addressLine)
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

if __name__ == "__main__":
    # print(x.pubkey_bytes)
    # print(x.address)
    # scanBlockchain("Zoey")
    main()
