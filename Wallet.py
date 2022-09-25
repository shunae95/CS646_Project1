"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-21
"""
import os
from os.path import exists
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

class Wallet:
    """
    Creates an instance of a wallet. Will read the wallet's existing private key
    or create a new one if one does not already exist.
    """
    def __init__(self):
        pw = 'mypassword' # No password needed at this stage in the project, so default set
        self.password = pw.encode("utf-8")
        self.dirName = os.path.dirname(__file__) # Get current folder
        self.pemFileName = f"{self.dirName}\\privkey.pem" 
        self.__privkey = self.getOrCreatePem() 
        self.pubkey = self.__privkey.public_key()
        self.pubkey_bytes = self.getPubKeyBytes() # May not need this since we don't have to store it
        self.address = self.getOrCreateAddress()

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


if __name__ == "__main__":
    x = Wallet()
    print(x.pubkey_bytes)
    print(x.address)
