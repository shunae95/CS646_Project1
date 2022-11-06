import json
import binascii
import socket
import time
import threading
import Wallet
from math import ceil, log
from Transaction import Transaction
from Block import Block
import os
import hashlib
from random import random
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

TRANSACTIONS_NEEDED_FOR_BLOCK = 1
SELECTED_PORT = 2001
ALTERNATIVE_NODE = 2000
mining = False
class Node:
    def __init__(self):
        self.wallet = Wallet.Wallet()
        self.getOrCreateTxnDir()
        
    def getOrCreateTxnDir(self):
        dirName = os.path.dirname(__file__)# Variable to gain easy access to directory of current folder
        # transactions = [] # Array that stores transactions
        # addingTransactions = True # Variable that continues the loop if we are adding transactions
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
        
        try:
            os.mkdir(dirName + "/forked") # Try to create the pending directory.
        except FileExistsError:
            pass
            print("Forked folder exists.")
        
        
    def addPendingTransaction(self, transaction):
        dirName = os.path.dirname(__file__)# Variable to gain easy access to directory of current folder
        if not os.path.exists(f"{dirName}/pending/{self.encode(transaction)}.json"):
            with open(f"{dirName}/pending/{self.encode(transaction)}.json","w") as f:
                f.write(transaction)
    
    def addConfirmedTransaction(self, transaction):
        dirName = os.path.dirname(__file__)# Variable to gain easy access to directory of current folder
        if not os.path.exists(f"{dirName}/processed/{self.encode(transaction)}.json"):
            with open(f"{dirName}/processed/{self.encode(transaction)}.json","w") as f:
                f.write(transaction)

    def encode(self, string):
        # Gets the JSON string and returns its SHA256 hash
        # Function turns string into bytes before hashing, then it follows up with hexdigest to turn it back into a string.
        # Input: {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        # Output: 57bc6f8255b180cbaf73f286b107be0506713b32cfe8f41af29e5c1e17f8ca6d
        return hashlib.sha256(str.encode(string)).hexdigest()

# def download():
#     while True:
#         try:
#             down = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             down.bind((S))

#         except ConnectionRefusedError:
#             print("Could not connect to other node, retrying in 15 seconds.")
#             time.sleep(15)
#         except ConnectionResetError:
#             print("Lost connection to other node, reestablishing in 15 seconds.")
#             time.sleep(15)


def grabber(path: str) -> list:
    string: str
    l = []
    with open(path, "r") as f:
        string = f.read()
    
    l = string.split("[")[1].split("]")[0].split("},{")
    returnList = []
    for i in range(len(l)):
        abomination = l[i].split("\"content\":")[1]
        if abomination.endswith("}}"):
            abomination=abomination[:-1]
        returnList.append(abomination)
        # print(abomination)
    return returnList


def hashrootCreator() -> list:
    dirName = os.path.dirname(__file__)
    transactions = []
    files = [file for file in os.scandir(f"{dirName}/processed") if file.name.endswith(".json")]
    for file in files:
        with open(file.path, "r") as f:
            transactions.append(Transaction(f.read()))
    transactions.sort(key=transactionSort)
    encodedArray = list(map(Transaction.toEncodedJSON, transactions))
    hash = hashroot(encodedArray)
    with open(f"{dirName}/hashroot.txt", "w") as f:
        f.write(hash)
    
        
    

def hashroot(arr:list, num=0, debug=False) -> str:
    length = len(arr)
    exp = log(length, 2)
    while exp != ceil(exp):
        arr.append(arr[-1])
        length = len(arr)
        exp = log(length, 2)
    leftHalf = arr[:length//2]
    rightHalf = arr[length//2:]
    if debug:
        print(f"Left {num}: {leftHalf}")
        print(f"Right {num}: {rightHalf}")
    if exp == 1:
        return hashlib.sha256((hashlib.sha256(leftHalf[0].encode()).hexdigest()+hashlib.sha256(rightHalf[0].encode()).hexdigest()).encode()).hexdigest()
    else:
        l = hashroot(leftHalf, num + 1).encode()
        r = hashroot(rightHalf, num + 1).encode()
        return hashlib.sha256((l+r)).hexdigest()
 
    

def storeSignature(trxBytes:bytes, signature, decode=True):
    dirName = os.path.dirname(__file__)
    hash = hashlib.sha256(trxBytes).hexdigest()
    # print(trxBytes)
    if decode:
        with open(f"{dirName}/signatures.json", "a") as f:
            f.write("{" + f'"hash":"{hash}","signature":"{binascii.b2a_hex(signature).decode()}"' + "}\n")
    else:
        with open(f"{dirName}/signatures.json", "a") as f:
            f.write("{" + f'"hash":"{hash}","signature":"{signature}"' + "}\n")
def update(data):

    while True:
        try:

            r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r.connect((socket.gethostname(), ALTERNATIVE_NODE))
            # print(f"Data: {data}")
            print("Connected to other node.", end=" ")
            r.sendall(bytes(f"minerUpdate__||__{data}","utf-8"))
            r.close()
            print("New data sent.")
            return
                # while True:
                #     data = r.recv(4096)
                #     if len(data) != 0:
                #         print(data)
                #     r.close()

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
        print("Creating a new block.", end=" ")
        processingToBlock(Node)
        hashrootCreator()

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


def processingToBlock(Node: Node):
    global mining
    mining = True
    dirName = os.path.dirname(__file__)
    buildingBlock = True
    while buildingBlock:
        transactions = grabPendingTransactions()
        transactions.insert(0, Transaction('{' + f'"timestamp":{int(time.time())},"from":"Coinbase","to":"' + Node.wallet.getOrCreateAddress() + f'","amount":{random()}' + '}'))
        Node.addPendingTransaction(transactions[0].toJSON())
        signature = Node.wallet.signTransaction(transactions[0])
        
        # update(transactions[0].toJSON().encode() + b"__" + binascii.b2a_hex(signature))
        addingToBlock = True # Variable to manage the adding to the block loop
        height = 0 # Starting height 
        # while addingToBlock:
        while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
            height += 1 
            
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
        data = block.generateData()
        if block.valid and not os.path.exists(dirName + f"/B_{height}.json"):
            value = int(data.split('\"height\":')[1].split(",")[0])
            if height != value:
                with open(f"{dirName}/forked/B_{value}.json", "w") as f:
                    f.write(data)
                    update(transactions[0].toJSON().encode() + b"__" + binascii.b2a_hex(signature))
                    storeSignature(transactions[0].toJSON().encode(), signature)

                    update(data)
            else:
            #     for file in [f for f in os.listdir(dirName + "/forked")]:

            #         os.remove(dirName+"/forked/"+file)
            
                # byteString = b"__" 
                # transactionList = []
                # for transaction in [f for f in os.listdir(dirName + "/processed") if f.endswith(".json")]:
                #     byteString += transaction.encode() + b"__"
                # for block in  [f for f in os.listdir(dirName) if f.endswith(".json") and f.startswith("B_")]:
                #     l = grabber(dirName+"/"+block)
                #     for entry in l:
                #         transactionList.append(entry)

                #     byteString += block.encode() + b"__"
                # print(f"Transaction List: {transactionList}")
                # transactionSync = b"syncT__"
                # for entry in transactionList:
                #     transactionSync += entry.encode() + b"__"
                # update(transactionSync)
                # update(b"sync" + byteString)
                for block in  [f for f in os.listdir(dirName) if f.endswith(".json") and f.startswith("B_")]:
                    with open(f"{dirName}/{block}","r") as fread:
                        update(b"syncB" + b"__" + block.encode() + b"__" + fread.read().encode())
            with open(f"{dirName}/B_{value}.json", "w") as f:
                f.write(data)
                update(transactions[0].toJSON().encode() + b"__" + binascii.b2a_hex(signature))
                storeSignature(transactions[0].toJSON().encode(), signature)

                update(data)    
        else: # Remove processed coinbase since the block is no longer valid
            os.remove(f"{dirName}/processed/{transactions[0].toEncodedJSON()}.json")
            # if (len([f for f in os.listdir(dirName+"/forked") if f.endswith(".json")]) != 0):
            #     for file in [f for f in os.scandir(dirName+"/forked") if f.name.endswith(".json")]:
            #         os.rename(file.path,file.path.split("/forked/")[0] + file.path.split("/forked")[1])
            # addingToBlock = False
        if len([file for file in os.listdir(dirName+'/pending') if file.endswith('.json')]) == 0:
            buildingBlock = False
    hashrootCreator()
    mining = False
    print("Pending transctions added to block.")

def scanBlockchain(address: str) -> tuple:
    balance = 0
    latestBlock = 0
    dirName = os.path.dirname(__file__)
    # for file in os.scandir(dirName):
    #     if file.name.startswith("B_") and file.name.endswith(".json"):
    #         # print(file.name)
    #         blockNumber = int(file.name.lstrip("B_").rstrip(".json"))
    #         if blockNumber > latestBlock:
    #             latestBlock = blockNumber
    #         with open(file.path, "r") as f:
    #             jsonString = f.read()
    #         jsonSplit = " ".join(jsonString.split("\"body\":"))
    #         contentSplit = jsonSplit.split("\"content\":")

    #         for i in range(len(contentSplit)):
    #             if i == 0: 
    #                 # print(f"Number of trnx: {len(contentSplit)-1}")
    #                 continue
    #             elif i < len(contentSplit)-1:
    #                 contentSplit[i] = contentSplit[i].split("},{\"hash\"")[0]
    #             else:
    #                 contentSplit[i] = contentSplit[i].split("}]}")[0]
                
    #             fromToFields = contentSplit[i].split(",")[1:3]
    #             fromField = fromToFields[0].split(":")[1].strip('"')
    #             toField = fromToFields[1].split(":")[1].strip('"')
    #             amountField = float(contentSplit[i].split(",")[3].split(":")[1].strip("}"))
    #             # print(f"From: {fromField}, To: {toField}, Amount: {amountField}")
    #             if fromField == address:
    #                 balance -= amountField
    #             if toField == address:
    #                 balance += amountField
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
    for file in os.scandir(dirName + "/processed"):
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
    # print(f"Final Balance for {address}: {balance}")
    return (balance, latestBlock)


if __name__ == "__main__":
    x = Node()
    print(f"Wallet: {x.wallet.getOrCreateAddress()}")
    dirName = os.path.dirname(__file__)
    # downThread = threading.Thread(target=update, daemon=True)
    # downThread.start()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', SELECTED_PORT))
    s.listen(5)

    # time.sleep(5)
    # r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # r.recv(2048)
    while True:
        if len(os.listdir(f"{dirName}/processed"))> 1:
            hashrootCreator()
        try:
            pass
            # r.connect((socket.gethostname(), 2001))
            # r.recv(2048)
            # r.close()
        except TimeoutError:
            print("No data incoming.")
        client, address = s.accept()
        # client.sendall((bytes("Port 2000", "utf-8")))
        data =  client.recv(2048000000)
        

        if len(data) > 0 and data.startswith(b"minerUpdate__||__"):
            # print(data)
            usefulData = data.split(b"__||__")[1].decode().lstrip("b").strip("'")
            # print("\n\n\n")
            # print(usefulData)
            if usefulData.startswith("{\"timestamp\""):
                # print(usefulData.split("__"))
                trnx = usefulData.split("__")
                # print(f"TRX[0]: {trnx[0]}")
                # print(f"TRX[1]: {trnx[1]}")
                if '\"from\":\"Coinbase\"' in trnx[0]:
                    x.addConfirmedTransaction(trnx[0])
                    # print("Coinbase\n\n")
                else:
                    x.addPendingTransaction(trnx[0])
                storeSignature(trnx[0].encode(), trnx[1], decode=False)
                # print(f"Useful: {usefulData}")

                # storeSignature(usefulData.encode())
            elif usefulData.startswith("{\"header\""):
                dirName = os.path.dirname(__file__)
                for file in os.scandir(dirName+"/pending/"):
                    if file.name[:-5] in usefulData:
                        os.rename(file.path, dirName+"/processed/"+file.name)
                addingToBlock = True # Variable to manage the adding to the block loop
                height = 0 # Starting height 
                value = int(usefulData.split('\"height\":')[1].split(",")[0])
                if height != value:
                    while addingToBlock:
                        with open(f"{dirName}/B_{value}.json", "w") as f: 
                            f.write(usefulData)
                            addingToBlock = False
                else:
                    while addingToBlock:
                        # while os.path.exists(dirName + f"/B_{height}.json"): # If a block at the current height exists, increment one
                        #     height += 1 
                        with open(f"{dirName}/forked/B_{value}.json", "w") as f: 
                            f.write(usefulData)
                            addingToBlock = False
            elif usefulData.startswith("sync"):
                if usefulData.startswith("syncT"):
                    trnxs = usefulData.split("__")
                    for entry in trnxs:
                        print(entry)
                else:
                    block = usefulData.split("__")[1]
                    data = usefulData.split("__")[2]
                    if os.path.exists(f"{dirName}/{block}"):
                        with open(f"{dirName}/{block}", "r") as reader:
                            contents = reader.read()
                            if data.split("\"Coinbase\",\"to\":\"")[1].split("\",\"amount\"")[0] not in contents:
                                reader.close()
                                with open(f"{dirName}/{block}", "w") as xreader:
                                    xreader.write(data)
                    # with open(f"{dirName}/{block}", "w") as writer:
                    #     writer.write(data)
                print("SYNC")
                print(f"Useful: {usefulData}")
                hashrootCreator()
                # for block in [f for f in os.listdir(f"{dirName}") if f.startswith("B_") and f.endswith(".json")]:
                #     transactionList = grabber(f"{dirName}/{block}")
                # for entry in [f for f in os.listdir(f"{dirName}/processed") if f.endswith(".json")]:
                #     if entry[:-5] not in transactionList:
                #         os.remove(f"{dirName}/processed/{entry}")
            if not mining:# if len(os.listdir(dirName + "/pending")) == 0: # I do not know the point of this right here, it will only activate when pending is empty but thats pointless since why would you want to check for a new block then...
                threading.Thread(target=checkToCreateNewBlock, args=(x,)).start()
                # print("It's not a boulder... it's a block.")

        elif len(data) > 0 and data.startswith(b"sync__||__"):
            print(f"Data sync: {data}")
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
                storeSignature(transaction, signature)
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
                    print(f"Amount: {amount}, actual:{scanBlockchain(fromAddress)[0]}")
                    client.sendall((bytes(str(-1), "utf-8")))
                    raise Exception("Account does not have enough funds.")
                x.addPendingTransaction(str(transaction, "UTF-8"))
                client.sendall((bytes(str(amount), "utf-8")))
                # print(f"Signature: {binascii.b2a_hex(signature).decode()}")
                update(transaction + b"__" + binascii.b2a_hex(signature))
                print("Transaction added to pending.")
                print(f"Mining Status: {mining}")
                if not mining:
                    threading.Thread(target=checkToCreateNewBlock, args=(x,)).start()


            except InvalidSignature:
                print("Error: Invalid signature on transaction. Canceling.")
            # except Exception as ex:
            #     print(f"Error: {ex.args[0]} Canceling.")
        elif len(data) > 0 and data.startswith(b"checkBalance__||__"):
            address = data.split(b"__||__")[1].decode("UTF-8")
            amount = scanBlockchain(address)[0]
            client.sendall(bytes(str(amount),"utf-8"))
        client.close()