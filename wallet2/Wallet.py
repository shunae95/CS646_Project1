2
"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-21

Code samples taken from python cryptography package documentation at https://cryptography.io/en/latest/.
"""
import os
from os.path import exists
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import random

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
        self.balance = random.randint(0,10)

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

# '''
# Function will check each block for the address and add/subtract the amounts found in transactions

# TODO: Make sure that the address is the exact address shown and not partial of another one found.
# (ex. A should not say true to AJ)
# '''
# def scanBlockchain(address: str):
#     balance = 0
#     dirName = os.path.dirname(__file__)
#     for file in os.scandir(dirName):
#         if file.name.startswith("B_") and file.name.endswith(".json"):
#             print(file.name)
#             with open(file.path, "r") as f:
#                 jsonString = f.read()
#             jsonSplit = " ".join(jsonString.split("\"body\":"))
#             contentSplit = jsonSplit.split("\"content\":")

#             for i in range(len(contentSplit)):
#                 if i == 0: 
#                     print(f"Number of trnx: {len(contentSplit)-1}")
#                     continue
#                 elif i < len(contentSplit)-1:
#                     contentSplit[i] = contentSplit[i].split("},{\"hash\"")[0]
#                 else:
#                     contentSplit[i] = contentSplit[i].split("}]}")[0]
                
#                 fromToFields = contentSplit[i].split(",")[1:3]
#                 fromField = fromToFields[0].split(":")[1].strip('"')
#                 toField = fromToFields[1].split(":")[1].strip('"')
#                 amountField = float(contentSplit[i].split(",")[3].split(":")[1].strip("}"))
#                 print(f"From: {fromField}, To: {toField}, Amount: {amountField}")
#                 if fromField == address:
#                     balance -= amountField
#                 elif toField == address:
#                     balance += amountField
#     print(f"Final Balance: {balance}")
#                 # if address in contents:
#                 #     print(f"IN - {file.name}")

if __name__ == "__main__":
    x = Wallet()
    # print(x.pubkey_bytes)
    print(x.address)
    # scanBlockchain("Zoey")
