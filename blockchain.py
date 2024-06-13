import datetime
import hashlib

DIFFICULTY = 5

class Block():
    def __init__(self, index, time, data, previousHash):
        self.index = index
        self.time = time
        self.data = data
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        blockHash = hashlib.sha256()
        blockHash.update(str(self.index).encode("utf-8") + str(self.time).encode("utf-8") + str(self.data).encode("utf-8") + str(self.previousHash).encode("utf-8") + str(self.nonce).encode("utf-8"))
        return blockHash.hexdigest()

    def mine(self, difficulty):
        while self.hash[0:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculateHash()

    def __str__(self):
        return f"Index:{self.index}\nTime:{self.time}\nData:{self.data}\nNonce:{self.nonce}\nPrevious Hash:{self.previousHash}\nHash:{self.hash}"

class Blockchain():
    def __init__(self):
        self.__chain = [Block(0, datetime.datetime.now(), "The first block!", "0")]

    def addBlock(self, data):
        newBlock = Block(len(self.__chain), datetime.datetime.now(), data, self.__chain[-1].hash)
        newBlock.mine(DIFFICULTY)
        self.__chain.append(newBlock)

    def getBlock(self, index):
        return self.__chain[index]

    def isValid(self):
        for block in self.__chain:
            if block.index != 0 and block.previousHash != self.__chain[block.index - 1].calculateHash():
                return False
        return True

class User():
    def __init__(self, username, password, currency):
        self.__username = username
        self.__password = password
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        blockHash = hashlib.sha256()
        blockHash.update(str(self.__username).encode("utf-8") + str(self.__password).encode("utf-8"))
        return blockHash.hexdigest()

blockchain = Blockchain()
blockchain.addBlock("hello")
blockchain.addBlock("data")
blockchain.addBlock("Cool")
for i in range(0, blockchain.getBlock(-1).index + 1):
    print(blockchain.getBlock(i))
    print()
print(blockchain.isValid())

