"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-10-23

Code samples taken from python cryptography package documentation at https://cryptography.io/en/latest/.
"""
import os
import socket
import sys
from os.path import exists
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature
import base64
import json
import random

from Transaction import Transaction
from Block import Block
from Account import Account, searchForAccount

PORT_CHOICES = [2000,2001]
SELECTED_PORT = random.choice(PORT_CHOICES)


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
                if toField == address:
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
    newTransaction = Transaction(userWallet)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), SELECTED_PORT))
    dataList = [newTransaction.toBytes(), userWallet.signTransaction(newTransaction), userWallet.getPubKeyBytes()]
    # print(dataList[1])
    byteList = b'__||__'.join(dataList)
    print("Sending byteList:",byteList)
    s.sendall(byteList)
    m = s.recv(1024)
    print("Got back", m)
    # clean = float(data.decode("utf-8"))
    # if clean != -1:
    #     userWallet.account.balance += clean
    s.close()


def transactionSort(transaction: Transaction) -> int:
    return transaction.time


def menu(userWallet: Wallet):
    print(f"Selected Node: {SELECTED_PORT}")
    present = True
    while present:
        # try:
            print("1. \tCheck local wallet balance.")
            print("2. \tCheck wallet balance using address.")
            print("3. \tCreate a transaction.")
            print("4. \tExit application.")

            try:
                response = int(input("> "))
            except:
                print("Invalid Input. Please choose again.")
            
            if (response == 1):
                # print("IMPLEMENT SHOWING PENDING BALANCE AS WELL, THIS WOULD REQUIRE UPADTING THE ACCOUNTS JSON PER TRANSACTION")
                # print("PENDING ONLY DISPLAYS OUTGOING AND DOES NOT CONSIDER INCOMING TRANSACTIONS")
                # if userWallet.account.balance != scanBlockchain(userWallet.address)[0]:
                #     userWallet.account.balance = scanBlockchain(userWallet.address)[0]
                #     userWallet.account.pendingBalance = userWallet.account.balance
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((socket.gethostname(), SELECTED_PORT))
                message = bytes(f"checkBalance__||__{userWallet.address}","utf-8")
                s.sendall(message)
                data = s.recv(1024)
                s.close()
                userWallet.account.balance = float(data)

                print(f"Current balance for {userWallet.address}: {userWallet.account.balance}")
            elif (response == 2):
                address = input("Address: ")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((socket.gethostname(), SELECTED_PORT))
                message = bytes(f"checkBalance__||__{address}","utf-8")
                s.sendall(message)
                data = s.recv(1024)
                s.close()
                print(f"Current balance for {address}: {float(data)}")
            elif (response == 3):
                transactionCreation(userWallet)
                # accountDB = updateAccountDB(userWallet.account)
                # rewriteAddressDatabase()
                # userWallet.balance, userWallet.latestBlock = scanBlockchain(userWallet.address) ?????? To update balance but latest block cannot really be updated since a newly created transaction will not be in a block yet
            elif (response == 4):                
                # userWallet.account.balance = userWallet.account.pendingBalance
                # rewriteAddressDatabase()
                print("Quitting application.")
                present = False
        # except InvalidSignature : 
        #     print("Invalid Signature for created transaction. Discarding transaction.")
      

def updateAccountDB(userAccount: Account):
    accountDB = Account.getAccList()
    for entry in accountDB:
        # print(f"{userAccount.address} - {entry.address}")
        if userAccount.address == entry.address:
            entry.balance = userAccount.balance
        else:
            entry.balance = float(scanBlockchain(entry.address)[0])
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

if __name__ == "__main__":
    main()
