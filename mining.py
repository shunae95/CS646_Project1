import time
import json
import hashlib
from Block import Block

target = "00"
block = Block(target, "NA")

block.header["timestamp"] = time.time()

previousHash = hashlib.sha256(previousHash)
previousHash = previousHash.hexdigest()
block.header["previousblock"] = previousHash

found = False
nonce = 0

while not found:
    block["Nonce: "] = nonce
    jsonvalue = json.dumps(block)
    print(jsonvalue)
    blockHash = hashlib.sha256(jsonvalue.encode("utf-8")).hexdigest()
    print(blockHash)
    if str(blockHash)[0:len(target)] == target:
        found = True
    nonce = nonce + 1 

def validateBlock(block, hash):
    jsonvalue = json.dumps(block)
    print(jsonvalue)
    blockHash = hashlib.sha256(jsonvalue.encode("utf-8")).hexdigest
    print(blockHash)
    if str(blockHash)[0:len(target)] == target and blockHash == hash:
        print("Valid block")
    else:
        print("Invalid block")

validateBlock(block, blockHash)