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
        self.header = '"header":{"height":'+ str(self.height) +f',"timestamp":{int(time.time())},"previousblock":"{self.prevHash}","hash":"'+ hash +'"}' #Header data format
        self.data = "{" + f'{self.header},{self.body}' + "}" #JSON string of header and body combined

    def generateHeader(self):
        self.generateBody()
        hash = hashlib.sha256(str.encode(self.body)).hexdigest() #Generating hash of body to include in header
        self.header = '"header":{"height":'+ str(self.height) +f',"timestamp":{int(time.time())},"previousblock":"{self.prevHash}","hash":"'+ hash +'"}'

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
if __name__ == "__main__":
    print(Block(2).data)