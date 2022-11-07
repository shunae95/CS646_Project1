"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-10-23

Code samples taken from python cryptography package documentation at https://cryptography.io/en/latest/.
"""
import json
import socket
import time
import threading
import Wallet
from Transaction import Transaction
from Block import Block
import os
import hashlib
from random import random
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

TRANSACTIONS_NEEDED_FOR_BLOCK = 3
SELECTED_PORT = 2001
ALTERNATIVE_NODE = 2000
# updateRequest = False
class Node:
    def __init__(self):
        self.wallet = Wallet.Wallet()
        self.getOrCreateTxnDir()
        
    def getOrCreateTxnDir(self):
        dirName = os.path.dirname(__file__)# Variable to gain easy access to directory of current folder
        try:
            os.mkdir(dirName + "/processed") # Try to create the processed directory
        except FileExistsError:
            pass
            print("Processed folder exists.")
        try:
            os.mkdir(dirName + "/pending") # Try to create the pending directory.
        except FileExistsError:
            pass
            print("Pending folder exists.")

    def addPendingTransaction(self, transaction):
        dirName = os.path.dirname(__file__)# Variable to gain easy access to directory of current folder
        if not os.path.exists(f"{dirName}/pending/{self.encode(transaction)}.json"):
            with open(f"{dirName}/pending/{self.encode(transaction)}.json","w") as f:
                f.write(transaction)

    def encode(self, string):
        # Gets the JSON string and returns its SHA256 hash
        # Function turns string into bytes before hashing, then it follows up with hexdigest to turn it back into a string.
        # Input: {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        # Output: 57bc6f8255b180cbaf73f286b107be0506713b32cfe8f41af29e5c1e17f8ca6d
        return hashlib.sha256(str.encode(string)).hexdigest()


def update(data):
    """Sends transaction or block completion data to other miners."""
    while True:
        try:

            r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r.connect((socket.gethostname(), ALTERNATIVE_NODE))
            print("Connected to other node.", end="")
            r.sendall(bytes(f"minerUpdate__||__{data}","utf-8"))
            r.close()
            print("New data sent.")
            return

        except ConnectionRefusedError:
            print("Could not connect to other node, retrying in 15 seconds.")
            time.sleep(15)
        except ConnectionResetError:
            print("Lost connection to other node, reestablishing in 15 seconds.")
            time.sleep(15)

def checkToCreateNewBlock(Node):
    dirName = os.path.dirname(__file__)
    files = [(entry) for entry in os.listdir(dirName+"/pending") if entry.endswith(".json")]
    if len(files) >= TRANSACTIONS_NEEDED_FOR_BLOCK:
        print("Creating a new block.", end="")
        buildingNextBlock(Node)

def grabPendingTransactions() -> list:
    transactions = []
    dirName = os.path.dirname(__file__)+"/pending"
    for file in os.scandir(dirName):
        if not file.name.endswith(".json"):
            continue
        # print(file.name)
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


def buildingNextBlock(Node: Node):
    dirName = os.path.dirname(__file__)
    height = 0 # Starting height 
    while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
        height += 1 

    nonceFound = False
    nonce = 0
    start = time.time()

    while not nonceFound:
        transactions = grabPendingTransactions()
        transactions.insert(0, Transaction('{' + f'"timestamp":{int(time.time())},"from":"Coinbase","to":"' + Node.wallet.getOrCreateAddress() + f'","amount":{random()}' + '}'))
        Node.addPendingTransaction(transactions[0].toJSON())
        # update(transactions[0].toJSON())
        # addingToBlock = True # Variable to manage the adding to the block loop

        if height == 0: # If height is 0 then use the default previous hash
            block = Block(height, "NA", 0)
        else: # Else use the hash of the previous block.
            with open(f"{dirName}/B_{height-1}.json", "rb") as oldBlock:
                oldHash = hashlib.sha256(oldBlock.read()).hexdigest()
            block = Block(height, oldHash, nonce)
            
            for entry in transactions: # Add each pending transaction into the block's transaction array
                block.addTransaction(entry)

    # Search for nonce
        data = block.generateData()
        jsonvalue = json.dumps(data)
        blockhash = hashlib.sha256(jsonvalue.encode('utf-8')).hexdigest()
        if str(blockhash)[0:len(block.target)] == block.target:
            nonceFound = True
        nonce = nonce+1
    
    
    end = time.time()
    print("NONCE FOUND IN", end - start, "seconds")
    
    # Once found, write the block        
    with open(f"{dirName}/B_{height}.json", "w") as f: 
        f.write(data)

    # Send the new block to other miners
    update(data)
    
    # Move transactions in block from pending to processed
    block.completedTransactions = list(map(Transaction.toEncodedJSON, transactions))
    for file in os.scandir(dirName + "/pending"):
        if file.name[:-5] in block.completedTransactions:
            os.rename(dirName+"/pending/"+ file.name, dirName+"/processed/"+ file.name)
  
        
    print(f"Block {height} created")

def validateBlock(block, hash):
    target = "00"
    jsonvalue = json.dumps(block)
    print(jsonvalue)
    blockhash = hashlib.sha256(jsonvalue.encode('utf-8')).hexdigest()
    print(blockhash)
    if str(blockhash)[0:len(target)] == target and blockhash == hash:
        print("Block is valid")
        return True
    else:
        print("Block is invalid")
        return False

def scanBlockchain(address: str) -> tuple:
    balance = 0
    latestBlock = 0
    dirName = os.path.dirname(__file__)
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
    for file in os.scandir(dirName + "/pending"):
        if file.name.endswith(".json"):
            with open(file.path, "r") as f:
                jsonString = f.read()
            jsonSplit = jsonString.strip("{}").split(",")
            fromField = jsonSplit[1].split(":")[1].strip('"')
            toField = jsonSplit[2].split(":")[1].strip('"')
            # print(f"toField: {toField}")
            # print(f"Address: {address}")
            amountField = float(jsonSplit[3].split(":")[1])
            if fromField == address:
                balance -= amountField
            if toField == address:
                balance += amountField
    print(f"Final Balance for {address}: {balance}")
    return (balance, latestBlock)


if __name__ == "__main__":
    x = Node()
    print(f"Wallet: {x.wallet.getOrCreateAddress()}")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', SELECTED_PORT))
    s.listen(5)

    # time.sleep(5)
    # r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # r.recv(2048)
    while True:
        try:
            pass
        except TimeoutError:
            print("No data incoming.")
        client, address = s.accept()
        data = client.recv(4096)
        print("Got some data", data)
        

        if len(data) > 0 and data.startswith(b"minerUpdate__||__"):
            # print(data)
            usefulData = data.split(b"__||__")[1].decode().lstrip("b").strip("'")
            # print("\n\n\n")
            # print(usefulData)
            if usefulData.startswith("{\"timestamp\""): # it's a transaction
                x.addPendingTransaction(usefulData)
            elif usefulData.startswith("{\"header\""):  # it's a block
                dirName = os.path.dirname(__file__)
                 # Validate the block
                jsonvalue = json.dumps(usefulData)
                blockhash = hashlib.sha256(jsonvalue.encode('utf-8')).hexdigest()
                if validateBlock(usefulData, blockhash) == True:
                    # Move pending transactions to processed
                    for file in os.scandir(dirName+"/pending/"):
                        if file.name[:-5] in usefulData:
                            os.rename(file.path, dirName+"/processed/"+file.name)
                addingToBlock = True # Variable to manage the adding to the block loop
                height = 0 # Starting height 
                while addingToBlock:
                    while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
                        height += 1 
                    with open(f"{dirName}/B_{height}.json", "w") as f: 
                        f.write(usefulData)
                        addingToBlock = False
                # print("It's not a boulder... it's a block.")
        elif len(data) > 0 and not data.startswith(b"checkBalance__||__"):
            # print(f"Received data from wallet: {data}")
            dataSplit = data.split(b"__||__")
            # print(dataSplit[0])
            transaction = dataSplit[0]
            signature = bytes(dataSplit[1])
            try:
                encodeStr = x.encode(str(transaction, "UTF-8"))
                dirName = os.path.dirname(__file__)
                if os.path.exists(f'{dirName}/pending/{encodeStr}.json') or os.path.exists(f'{dirName}/processed/{encodeStr}.json'):
                    raise Exception("Transaction already received.")

                load_pem_public_key(dataSplit[2]).verify(signature, transaction, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
                print("Signature confirmed.", end=" ")
                transactionSplit = str(transaction, "UTF-8").strip("{}").split(",")
                results = []
                for i in range(len(transactionSplit)):
                    if i == 0:
                        results.append(int(transactionSplit[i].split(":")[1].strip('"')))
                    elif i == 1:
                        fromAddress = transactionSplit[i].split(":")[1].strip('"')
                        if len(fromAddress) != 64:
                            raise Exception("Transaction contained an invalid address.")
                        results.append(transactionSplit[i].split(":")[1].strip('"')) 
                    elif i == 2:
                        toAddress = transactionSplit[i].split(":")[1].strip('"')
                        if len(toAddress) != 64:
                            raise Exception("Transaction contained an invalid address.")
                        results.append(transactionSplit[i].split(":")[1].strip('"')) 
                    elif i == 3:
                        try:
                            amount = float(transactionSplit[i].split(":")[1].strip('"'))
                            if amount <= 0:
                                raise ValueError
                            results.append(amount)
                        except ValueError:
                            raise Exception("Transaction did not contain a valid amount.")
                    else:
                        raise Exception("Transaction contained too many parameters.")
                print("Transaction data validated.", end=" ")
                # print(transactionSplit)
                # print(results)
                # print(f"Pre-transaction balance: {scanBlockchain(fromAddress)[0]}", end="")
                if scanBlockchain(fromAddress)[0] < amount:
                    client.sendall((bytes(str(-1), "utf-8")))
                    raise Exception("Account does not have enough funds.")
                x.addPendingTransaction(str(transaction, "UTF-8"))
                client.sendall((bytes(str(amount), "utf-8")))
                update(transaction)
                print("Transaction added to pending.")
                checkToCreateNewBlock(x)

            except InvalidSignature:
                print("Error: Invalid signature on transaction. Canceling.")
           
        elif len(data) > 0 and data.startswith(b"checkBalance__||__"):
            address = data.split(b"__||__")[1].decode("UTF-8")
            amount = scanBlockchain(address)[0]
            client.sendall(bytes(str(amount),"utf-8"))
        client.close()