"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-21
"""
import os
from os.path import exists as file_exists
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

class Wallet:
    def __init__(self):
        pw = 'mypassword'
        self.password = pw.encode("utf-8")
        self.dirName = os.path.dirname(__file__) # Get current folder
        self.pemFileName = f"{self.dirName}\\privkey.pem" 
        self.privkey = self.getOrCreatePem() 
        self.pubkey = self.privkey.public_key()
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
        pem_exists = file_exists(self.pemFileName)
        if pem_exists == False:
            self.createPem()
        with open(self.pemFileName,"rb") as f:
            privkey = serialization.load_pem_private_key(
            f.read(),
            password=self.password,
            )
        return privkey

    def getOrCreateAddress(self):
        pub_key_bytes = self.pubkey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
        )
        addr = hashlib.sha256(base64.b64decode(pub_key_bytes)).hexdigest()
        return addr


if __name__ == "__main__":
    x = Wallet()
    print(x.pubkey)
    print(x.privkey)
    print(x.address)
