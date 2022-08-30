from time import time
import hashlib

class Transaction:
    def __init__(self, _from, _to, _amount):
        self._timestamp = int(time()) 
        self._from = _from
        self._to = _to
        self._amount = _amount # Casting to float, I do not think the assignment specified.

    def toJSON(self):
        # Builds string in same format as example
        # {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        return "{" + f'"timestamp":{self._timestamp},"from":"{self._from}","to":"{self._to}","amount":{self._amount}' + "}"
    
    def toEncodedJSON(self):
        # Gets the JSON string and returns its SHA256 hash
        # Function turns string into bytes before hashing, then it follows up with hexdigest to turn it back into a string.
        # Input: {"timestamp":1660791892,"from":"me","to":"you","amount":100000}
        # Output: 57bc6f8255b180cbaf73f286b107be0506713b32cfe8f41af29e5c1e17f8ca6d
        return hashlib.sha256(str.encode(self.toJSON())).hexdigest()

if __name__ == "__main__":

    _from = input("From: ")
    _to = input("To: ")
    _amount = input("Amount: ")
    x = Transaction(_from, _to, _amount)
    print(x.toEncodedJSON())