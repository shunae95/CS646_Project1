"""
We Tiara King, AJ Nettles, and Leigh Allison declare that we have completed this computer code in accordance with the UAB Academic Integrity Code and the UAB CS Honor Code.  
We have read the UAB Academic Integrity Code and understand that any breach of the Code may result in severe penalties.	
Student signature(s)/initials: TK, AN, LA
Date: 2022-09-17
"""
import os
import hashlib
import time
class Block:
    def __init__(self, height, prevHash): #Only used if this is the initial block in chain.
        self.transactions = [] # Holds transaction objects
        self.completedTransactions = []
        self.body = '"body":[{"hash":"57bc6f8255b180cbaf73f286b107be0506713b32cfe8f41af29e5c1e17f8ca6d","content":{"timestamp":1660791892,"from":"me","to":"you","amount":100000}}]' #Body data format
        hash = hashlib.sha256(str.encode(self.body)).hexdigest() #Generating hash of body to include in header
        self.prevHash = prevHash
        self.height = height
        self.valid = True
        self.header = '"header":{"height":'+ str(self.height) +f',"timestamp":{int(time.time())},"previousblock":"{self.prevHash}","hash":"'+ hash +'"}' #Header data format
        self.data = "{" + f'{self.header},{self.body}' + "}" #JSON string of header and body combined

    def generateHeader(self):
        self.generateBody()
        hash = hashlib.sha256(str.encode(self.body)).hexdigest() #Generating hash of body to include in header
        print(int(time.time()))
        proof = self.proof(self.body)
        self.header = '"header":{"height":'+ str(self.height) +f',"timestamp":{int(time.time())},"previousblock":"{self.prevHash}","hash":"'+ hash +'","proof":' + f"{proof}" + '}'

    def generateBody(self):
        content = ""
        subsequentRun = False
        
        for entry in self.transactions:
            if subsequentRun:
                content += "},{"
                subsequentRun = False
            content += f'"hash":"{entry.toEncodedJSON()}","content":' + entry.toJSON()
            self.completedTransaction(entry.toEncodedJSON())
            self.completedTransactions = [entry]
            subsequentRun = True
        
        self.body = '"body":[{'+ content +'}]'
    
    def generateData(self):
        self.generateHeader()
        self.data = "{" + f'{self.header},{self.body}' + "}" #JSON string of header and body combined
        return self.data

    def addTransaction(self, transaction):
        self.transactions.append(transaction)

    def completedTransaction(self, hash):
        self.completedTransactions.append(hash)

    def proof(self, text) -> int:
        target = 250000000000000000000000000000000000000000000000000000000000000000000000000
        # target = 5500000000000000000000000000000000000000000000000000000000000000000000 some minutes
        # target = 550000000000000000000000000000000000000000000000000000000000000000000 abount 1-4 Minutes
        running = True
        nonce = 0
        print("Block started.")
        while running:
            string = f"{text}{nonce}"
            hash = hashlib.sha256(string.encode()).hexdigest()
            value = int(hash, base=16)
            if value < target:
                # print(f"{string} - {hash} - {value}")
                print("PoW completed.")
                running = False
            else:
                nonce += 1
            if os.path.exists(os.path.dirname(__file__) + f"/B_{self.height}.json"):
                self.valid = False
                print("Block already exists.")
                return -1
        print("Block completed.")
        return nonce
    
if __name__ == "__main__":
    print(Block(0, "NA").data)